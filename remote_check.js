const fs = require('fs');
const html = fs.readFileSync('E:/project/team-share-public/remote_check.html', 'utf-8');

// Extract the last script block
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/g);
const lastScript = scriptMatch[scriptMatch.length - 1].replace(/<script>|<\/script>/g, '');

// Mock document and marked
global.document = {
  getElementById: (id) => {
    if (id === 'article') {
      return {
        innerHTML: '',
        querySelectorAll: () => []
      };
    }
    if (id === 'lightbox') {
      return {
        classList: { add: () => {}, remove: () => {} },
        addEventListener: () => {},
        style: {}
      };
    }
    if (id === 'lightbox-img') {
      return {
        src: '',
        style: {},
        classList: { add: () => {}, remove: () => {} },
        addEventListener: () => {}
      };
    }
    if (id === 'lightbox-close') {
      return { addEventListener: () => {} };
    }
    return null;
  },
  querySelectorAll: () => [],
  body: { style: {} },
  addEventListener: () => {}
};

global.window = { addEventListener: () => {} };

// Load marked from CDN? Instead, mock it to inspect the markdown string
global.marked = {
  parse: (md) => {
    console.log('Markdown starts with:', md.slice(0, 50));
    console.log('Markdown length:', md.length);
    console.log('Has frontmatter:', md.includes('title:'));
    return '<h1>Test</h1>';
  }
};

try {
  eval(lastScript);
  console.log('Script executed without error');
} catch (e) {
  console.log('Script error:', e.message);
  console.log(e.stack);
}
