(function () {
  const config = window.PAGE_CONFIG;
  if (!config) {
    return;
  }

  const artboard = document.getElementById("artboard");
  const links = document.getElementById("page-links");
  const title = document.getElementById("page-title");
  const subtitle = document.getElementById("page-subtitle");

  title.textContent = config.title;
  subtitle.textContent = config.subtitle || "";

  artboard.classList.toggle("with-phone", Boolean(config.phoneFrame));
  artboard.style.aspectRatio = `${config.designWidth} / ${config.designHeight}`;

  for (const layer of config.layers) {
    const image = document.createElement("img");
    image.className = "artboard-layer";
    image.src = layer.src;
    image.alt = layer.alt || "";
    image.style.left = `${(layer.x / config.designWidth) * 100}%`;
    image.style.top = `${(layer.y / config.designHeight) * 100}%`;
    image.style.width = `${(layer.width / config.designWidth) * 100}%`;
    image.style.height = `${(layer.height / config.designHeight) * 100}%`;
    artboard.appendChild(image);
  }

  for (const hotspot of config.hotspots || []) {
    const link = document.createElement("a");
    link.className = `artboard-hotspot ${hotspot.className || ""}`.trim();
    link.href = hotspot.href || "#";
    link.setAttribute("aria-label", hotspot.label || "interactive hotspot");
    link.style.left = `${(hotspot.x / config.designWidth) * 100}%`;
    link.style.top = `${(hotspot.y / config.designHeight) * 100}%`;
    link.style.width = `${(hotspot.width / config.designWidth) * 100}%`;
    link.style.height = `${(hotspot.height / config.designHeight) * 100}%`;

    if (hotspot.back) {
      link.addEventListener("click", function (event) {
        if (window.history.length > 1) {
          event.preventDefault();
          window.history.back();
        }
      });
    }

    const label = document.createElement("span");
    label.className = "sr-only";
    label.textContent = hotspot.label || "interactive hotspot";
    link.appendChild(label);
    artboard.appendChild(link);
  }

  for (const item of config.nav || []) {
    const link = document.createElement("a");
    link.className = `page-link ${item.id === config.id ? "active" : ""}`.trim();
    link.href = item.href;
    link.textContent = item.label;
    links.appendChild(link);
  }
})();
