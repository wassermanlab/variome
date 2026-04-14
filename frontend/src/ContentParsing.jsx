import Markdown from "react-markdown";
import _ from "lodash";
import { useState, useEffect } from "react";

// Pre-import a comprehensive set of MUI icons so they are included in the
// bundle and can be made available to ContentConfiguration.js at runtime.
// ContentConfiguration.js lives in public/ and is loaded as a blob URL, so
// the browser cannot resolve bare specifiers like "@mui/icons-material" on its
// own.  We expose these icons on window.__variomeIcons and transform the
// import statement in the fetched source before executing it.
import {
  Article,
  ChevronLeft,
  ChevronRight,
  ContactMail,
  Description,
  Email,
  Gavel,
  HelpCenter,
  Home as HomeIcon,
  Info,
  Login,
  Menu as MenuIcon,
  Person,
  Phone,
  Rule,
  Settings,
  Star,
} from "@mui/icons-material";

const _muiIcons = {
  Article,
  ChevronLeft,
  ChevronRight,
  ContactMail,
  Description,
  Email,
  Gavel,
  HelpCenter,
  Home: HomeIcon,
  Info,
  Login,
  Menu: MenuIcon,
  Person,
  Phone,
  Rule,
  Settings,
  Star,
};

// Make the icon map available as a global so the transformed
// ContentConfiguration.js module can reference it at runtime.
window.__variomeIcons = _muiIcons;

/**
 * Replace `import { X, Y as Z } from "@mui/icons-material"` (possibly
 * spanning multiple lines) with a destructuring from window.__variomeIcons.
 * This lets ContentConfiguration.js continue to use the normal MUI import
 * syntax even though it is evaluated as a blob URL module where bare
 * specifiers cannot be resolved by the browser.
 */
function _transformMuiImports(source) {
  return source.replace(
    /import\s*\{([^}]+)\}\s*from\s*["']@mui\/icons-material["']\s*;?/gs,
    (_, imports) => {
      const fields = imports
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean)
        .map((s) => {
          const [orig, alias] = s.split(/\s+as\s+/).map((p) => p.trim());
          return alias ? `${orig}: ${alias}` : orig;
        })
        .join(", ");
      return `const { ${fields} } = window.__variomeIcons ?? {};`;
    },
  );
}

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
  const rawConfigCode = await configResponse.text();
  const configCode = _transformMuiImports(rawConfigCode);
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
