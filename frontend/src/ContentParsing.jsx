
import Markdown from 'react-markdown'
import _ from 'lodash';
import IconMap from '../content/ContentConfiguration';

const markdownContent = import.meta.glob('../content/*.md', { 
  eager: true, 
  query: "?raw"
});

const HomeContent = _.fromPairs(_.map(_.toPairs(import.meta.glob('../content/Home/*.md', {
  eager: true,
  query: "?raw"
})), ([key, value]) => {
  return [key.split('/').pop().split('.')[0], value.default];
}));

var Content = [];

_.toPairs(markdownContent).forEach(([key, value]) => {
  var name = key.split('/').pop().split('.')[0];
  var nameLower = _.replace(name.toLowerCase(),/\s+/g, '-');// ' ', '-');
  Content.push({
    name,
    content: <Markdown>{value.default}</Markdown>,
    urlPath: nameLower,
    icon: _.get(IconMap, name, IconMap.default)
  });
});

Content = _.sortBy(Content, c => {
  return _.indexOf(_.keys(IconMap), c.name);
});

export {Content, HomeContent};