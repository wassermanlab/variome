import Markdown from "react-markdown";
import _ from "lodash";
import { useState, useEffect } from "react";

// Module-level cache so content is only fetched once
let _content = null;
let _homeContent = null;
let _homeImageStyle = null;
let _loadingPromise = null;

async function _fetchAllContent() {
  // Dynamically load ContentConfiguration.js from the public root at runtime.
  // Using fetch + blob URL so Vite does not attempt to resolve the module at
  // build time (public/ assets are not bundled).
  const configResponse = await fetch("/ContentConfiguration.js");
  const configCode = await configResponse.text();
  const blob = new Blob([configCode], { type: "application/javascript" });
  const blobUrl = URL.createObjectURL(blob);
  let IconMap, HomeImageStyle;
  try {
    ({ IconMap, HomeImageStyle } = await import(/* @vite-ignore */ blobUrl));
  } finally {
    URL.revokeObjectURL(blobUrl);
  }
  _homeImageStyle = HomeImageStyle || {};

  // Fetch each page's markdown file based on IconMap keys
  const pageNames = _.keys(IconMap).filter((key) => key !== "default");
  const pageEntries = (
    await Promise.all(
      pageNames.map(async (name) => {
        try {
          // Markdown files are served from the public root (e.g. /About.md)
          const response = await fetch(`/${name}.md`);
          if (!response.ok) return null;
          const text = await response.text();
          // URL slug uses the lowercase-with-dashes form of the name
          const urlPath = _.replace(name.toLowerCase(), /\s+/g, "-");
          return {
            name,
            content: <Markdown>{text}</Markdown>,
            urlPath,
            icon: _.get(IconMap, name, IconMap.default),
          };
        } catch (e) {
          console.warn(`Failed to load content for "${name}":`, e);
          return null;
        }
      }),
    )
  ).filter(Boolean);

  // Preserve the ordering defined in IconMap
  _content = _.sortBy(pageEntries, (c) => _.indexOf(pageNames, c.name));

  // Fetch Home section markdown files
  const homeFileNames = ["full title", "intro", "image", "footer image"];
  _homeContent = {};
  await Promise.all(
    homeFileNames.map(async (filename) => {
      try {
        const response = await fetch(`/Home/${filename}.md`);
        if (response.ok) {
          _homeContent[filename] = await response.text();
        }
      } catch (e) {
        console.warn(`Failed to load home content "${filename}":`, e);
      }
    }),
  );

  return {
    content: _content,
    homeContent: _homeContent,
    homeImageStyle: _homeImageStyle,
  };
}

// Kick off loading eagerly as soon as this module is imported
function initContent() {
  if (!_loadingPromise) {
    _loadingPromise = _fetchAllContent();
  }
  return _loadingPromise;
}

initContent();

/**
 * Hook that returns all site content.  Loading begins when the module is first
 * imported so content is usually ready by the time components render.
 *
 * @returns {{ content: Array, homeContent: Object, homeImageStyle: Object, loading: boolean }}
 */
export function useContent() {
  const [state, setState] = useState({
    content: _content || [],
    homeContent: _homeContent || {},
    homeImageStyle: _homeImageStyle || {},
    loading: _content === null,
  });

  useEffect(() => {
    if (_content === null) {
      initContent()
        .then(({ content, homeContent, homeImageStyle }) => {
          setState({ content, homeContent, homeImageStyle, loading: false });
        })
        .catch((err) => {
          console.error("Failed to load site content:", err);
          setState((prev) => ({ ...prev, loading: false }));
        });
    }
  }, []);

  return state;
}
