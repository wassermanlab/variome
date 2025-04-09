
import MarkdownIt from 'markdown-it';
import _ from 'lodash';


const markdownFiles = import.meta.glob('../content/*.md');

const md = new MarkdownIt();

const parseMarkdown = (markdownText) => {
  return md.render(markdownText);
};

const loadMarkdown = async () => {
  const sections = [];
  const loadedFiles = await Promise.all(
    _.toPairs(markdownFiles).map(([path, loader]) => {
      const fileName = path.split('/').pop().replace('.md', '');
      return loader().then((content) => {
        console.log("got content", content);
        return { 
          name: fileName, 
          html: parseMarkdown(content.default),
          content: content.default
        };
      }).catch(err => {
        console.error(`Error loading markdown file ${path}:`, err);
        return { 
          name: fileName, content: "" };
      });
    })
  );
  sections.push(...loadedFiles);
  return sections;
};

export { loadMarkdown};