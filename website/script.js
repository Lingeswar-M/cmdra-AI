const VERSION = "v1.0.0";

const version = document.getElementById("version");
const versionFooter = document.getElementById("version-footer");
const year = document.getElementById("year");

if (version) version.textContent = VERSION;
if (versionFooter) versionFooter.textContent = VERSION;
if (year) year.textContent = new Date().getFullYear();

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("show");
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll(".reveal").forEach((node, i) => {
  node.style.transitionDelay = `${Math.min(i * 60, 300)}ms`;
  observer.observe(node);
});
