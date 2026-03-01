import os
import shutil
from utils.fuzzy import best_match, normalize_text, similarity

# Base directory (Desktop for safety)
BASE_DIR = os.path.join(os.path.expanduser("~"), "Desktop")
HOME_DIR = os.path.expanduser("~")


def _safe_path(name):
    return os.path.join(BASE_DIR, name)


def _path_matches_type(path, want_dir=None):
    if want_dir is None:
        return True
    if want_dir:
        return os.path.isdir(path)
    return os.path.isfile(path)


def _path_stem(path):
    return os.path.splitext(os.path.basename(path))[0]


def _fuzzy_resolve_in_directory(root, name, want_dir=None, cutoff=0.78):
    if not root or not os.path.exists(root):
        return None

    query = normalize_text(name)
    if not query:
        return None

    best_path = None
    best_score = 0.0

    for current_root, dirs, files in os.walk(root):
        entries = dirs if want_dir is True else files if want_dir is False else (dirs + files)
        for entry in entries:
            candidate = os.path.join(current_root, entry)
            rel = normalize_text(os.path.relpath(candidate, root))
            base = normalize_text(entry)
            stem = normalize_text(os.path.splitext(entry)[0])

            if query in {rel, base, stem}:
                return candidate

            score = max(similarity(query, rel), similarity(query, base), similarity(query, stem))
            if score > best_score:
                best_score = score
                best_path = candidate

    if best_score >= cutoff:
        return best_path
    return None


def _fuzzy_resolve_existing(name, want_dir=None, cutoff=0.78):
    query = normalize_text(name)
    if not query:
        return None

    candidates = []
    roots = [root for root in _candidate_roots() if os.path.exists(root)]
    for root_index, root in enumerate(roots):
        if not os.path.exists(root):
            continue
        for current_root, dirs, files in os.walk(root):
            entries = dirs if want_dir is True else files if want_dir is False else (dirs + files)
            for entry in entries:
                path_str = os.path.join(current_root, entry)
                if not _path_matches_type(path_str, want_dir=want_dir):
                    continue

                rel_path = normalize_text(os.path.relpath(path_str, root))
                base_name = normalize_text(entry)
                stem_name = normalize_text(os.path.splitext(entry)[0])

                if query in {rel_path, base_name, stem_name}:
                    return path_str
                candidates.append(path_str)
                quick_score = max(similarity(query, entry), similarity(query, os.path.splitext(entry)[0]))
                if root_index == 0 and quick_score >= 0.92:
                    return path_str

    best_path = None
    best_score = 0.0
    for candidate in candidates:
        rel_variants = []
        root_bonus = 0.0
        for index, root in enumerate(roots):
            if normalize_text(candidate).startswith(normalize_text(root)):
                rel_variants.append(normalize_text(os.path.relpath(candidate, root)))
                if index == 0:
                    root_bonus = 0.03
        score = max(
            similarity(query, os.path.basename(candidate)),
            similarity(query, _path_stem(candidate)),
            max([similarity(query, rel) for rel in rel_variants], default=0.0),
        ) + root_bonus
        if score > best_score:
            best_score = score
            best_path = candidate

    if best_score >= cutoff:
        return best_path
    return None


def _normalize_destination(destination):
    value = normalize_text(destination)
    aliases = {
        "desktop": os.path.join(HOME_DIR, "Desktop"),
        "downloads": os.path.join(HOME_DIR, "Downloads"),
        "download": os.path.join(HOME_DIR, "Downloads"),
        "documents": os.path.join(HOME_DIR, "Documents"),
        "document": os.path.join(HOME_DIR, "Documents"),
        "pictures": os.path.join(HOME_DIR, "Pictures"),
        "picture": os.path.join(HOME_DIR, "Pictures"),
        "videos": os.path.join(HOME_DIR, "Videos"),
        "video": os.path.join(HOME_DIR, "Videos"),
    }
    if value in aliases:
        return aliases[value]
    alias_match, _ = best_match(value, list(aliases.keys()), cutoff=0.75)
    if alias_match:
        return aliases[alias_match]

    compact = value.replace(" ", "")
    if compact in {"ddrive", "d:", "d"}:
        return "D:\\"
    if compact in {"edrive", "e:", "e"}:
        return "E:\\"

    destination = destination.strip()
    if os.path.isabs(destination):
        return destination

    resolved = _resolve_existing_path(destination, want_dir=True)
    if resolved:
        return resolved

    return os.path.join(BASE_DIR, destination)


def _candidate_roots():
    roots = [
        os.getcwd(),
        os.path.join(HOME_DIR, "Desktop"),
        os.path.join(HOME_DIR, "Downloads"),
        os.path.join(HOME_DIR, "Documents"),
        os.path.join(HOME_DIR, "Pictures"),
        os.path.join(HOME_DIR, "Videos"),
    ]
    deduped = []
    seen = set()
    for root in roots:
        normalized = os.path.abspath(root)
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(root)
    return deduped


def _resolve_existing_path(name, want_dir=None):
    if not name:
        return None
    name = name.strip().strip('"').strip("'")
    if os.path.isabs(name) and os.path.exists(name) and _path_matches_type(name, want_dir=want_dir):
        return name
    cwd_candidate = os.path.join(os.getcwd(), name)
    if os.path.exists(cwd_candidate) and _path_matches_type(cwd_candidate, want_dir=want_dir):
        return cwd_candidate

    for root in _candidate_roots():
        if not os.path.exists(root):
            continue
        candidate = os.path.join(root, name)
        if os.path.exists(candidate) and _path_matches_type(candidate, want_dir=want_dir):
            return candidate

    return _fuzzy_resolve_existing(name, want_dir=want_dir)


def _apply_file_type(file_name, file_type=None):
    if "." in os.path.basename(file_name):
        return file_name
    if not file_type:
        return file_name

    mapping = {
        "text": ".txt",
        "txt": ".txt",
        "doc": ".doc",
        "docx": ".docx",
        "pdf": ".pdf",
        "json": ".json",
        "csv": ".csv",
        "python": ".py",
        "py": ".py",
    }
    ext = mapping.get(file_type.lower())
    if not ext:
        return file_name
    return f"{file_name}{ext}"


# 1. Create Folder
def create_folder(folder_name):
    try:
        path = _safe_path(folder_name)
        os.makedirs(path, exist_ok=True)
        return f"Folder '{folder_name}' created on Desktop."
    except Exception as e:
        return f"Error creating folder: {e}"


# 2. Create File
def create_file(file_name, folder_name="Desktop", content="", file_type=None):
    base = _normalize_destination(folder_name)
    os.makedirs(base, exist_ok=True)

    file_name = _apply_file_type(file_name.strip(), file_type=file_type)
    path = os.path.join(base, file_name)

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File '{file_name}' created in '{folder_name}'."
    except Exception as e:
        return f"Error creating file: {e}"


# 3. Delete Folder
def delete_folder(folder_name, confirm=False):
    path = _resolve_existing_path(folder_name, want_dir=True)

    if not confirm:
        return f"Please confirm deletion of folder '{folder_name}'. Type yes to continue."

    try:
        if path and os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)
            return f"Folder '{folder_name}' deleted successfully."
        return "Folder not found."
    except Exception as e:
        return f"Error deleting folder: {e}"


# 4. Delete File
def delete_file(file_name, confirm=False):
    path = _resolve_existing_path(file_name, want_dir=False)

    if not confirm:
        return f"Please confirm deletion of file '{file_name}'. Type yes to continue."

    try:
        if path and os.path.exists(path) and os.path.isfile(path):
            os.remove(path)
            return f"File '{file_name}' deleted successfully."
        return "File not found."
    except Exception as e:
        return f"Error deleting file: {e}"


# 5. Rename File
def rename_file(old_name, new_name):
    try:
        old_path = _resolve_existing_path(old_name, want_dir=False)
        if not old_path:
            return "File not found."

        new_path = os.path.join(os.path.dirname(old_path), new_name)
        os.rename(old_path, new_path)
        return f"Renamed '{old_name}' to '{new_name}'."
    except Exception as e:
        return f"Error renaming file: {e}"


# 6. Move File
def move_file(file_name, destination_folder):
    try:
        source = _resolve_existing_path(file_name)
        if not source:
            return "File or folder not found."

        destination = _normalize_destination(destination_folder)
        if not os.path.exists(destination):
            os.makedirs(destination, exist_ok=True)

        shutil.move(source, destination)
        if os.path.isdir(os.path.join(destination, os.path.basename(source))):
            return f"Moved folder '{file_name}' to '{destination_folder}'."
        return f"Moved '{file_name}' to '{destination_folder}'."
    except Exception as e:
        return f"Error moving file: {e}"


# 7. Move Folder
def move_folder(folder_name, destination_folder):
    try:
        source = _resolve_existing_path(folder_name, want_dir=True)
        if not source or not os.path.isdir(source):
            return "Folder not found."

        destination = _normalize_destination(destination_folder)
        if not os.path.exists(destination):
            os.makedirs(destination, exist_ok=True)

        shutil.move(source, destination)
        return f"Moved folder '{folder_name}' to '{destination_folder}'."
    except Exception as e:
        return f"Error moving folder: {e}"


# 8. List Files
def list_files():
    try:
        files = os.listdir(BASE_DIR)
        if not files:
            return "No files found on Desktop."
        return "Desktop Files:\n" + "\n".join(files)
    except Exception as e:
        return f"Error listing files: {e}"


# 9. Open File
def open_file(file_name):
    try:
        path = _resolve_existing_path(file_name, want_dir=False)

        if path and os.path.exists(path):
            os.startfile(path)
            return f"Opening '{file_name}'."
        return "File not found."
    except Exception as e:
        return f"Error opening file: {e}"


# 9b. Open File/Folder (optional destination)
def open_item(name, destination_folder=None):
    try:
        path = None
        clean_name = (name or "").strip().strip('"').strip("'")
        if not clean_name:
            return "Please provide a file or folder name."

        if destination_folder:
            destination = _normalize_destination(destination_folder)
            if os.path.exists(destination):
                direct = os.path.join(destination, clean_name)
                if os.path.exists(direct):
                    path = direct
                else:
                    path = _fuzzy_resolve_in_directory(destination, clean_name, want_dir=None)

        if not path:
            path = _resolve_existing_path(clean_name, want_dir=None)

        if path and os.path.exists(path):
            os.startfile(path)
            return f"Opening '{os.path.basename(path)}'."
        return "File or folder not found."
    except Exception as e:
        return f"Error opening file or folder: {e}"


# 10. Read File
def read_file(file_name):
    try:
        path = _resolve_existing_path(file_name, want_dir=False)

        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return content
        return "File not found."
    except Exception as e:
        return f"Error reading file: {e}"


# 11. Write to File (overwrite)
def write_file(file_name, content):
    try:
        path = _resolve_existing_path(file_name, want_dir=False) or _safe_path(file_name)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Written to '{file_name}'."
    except Exception as e:
        return f"Error writing file: {e}"


# 12. Organize Downloads
def organize_downloads():
    try:
        downloads = os.path.join(HOME_DIR, "Downloads")

        for file in os.listdir(downloads):
            file_path = os.path.join(downloads, file)

            if os.path.isfile(file_path):
                ext = file.split(".")[-1]
                folder = os.path.join(downloads, ext.upper())

                os.makedirs(folder, exist_ok=True)
                shutil.move(file_path, folder)

        return "Downloads organized by file type."
    except Exception as e:
        return f"Error organizing downloads: {e}"
