import EasyMDE from 'easymde';
import 'easymde/dist/easymde.min.css';
import DOMPurify from 'dompurify';

const TOOLBAR = [
  'bold', 'italic', 'heading', '|',
  'quote', 'unordered-list', 'ordered-list', '|',
  'link', 'image', 'table', 'code', '|',
  'undo', 'redo',
];

const PREVIEW_IMAGE_NAME = 'entry-preview-image';

const PURIFY_OPTIONS = {
  ADD_TAGS: ['iframe'],
  ADD_ATTR: ['allowfullscreen', 'frameborder'],
};

const MESSAGES = {
  empty: 'There is nothing to preview yet. '
    + 'Add a title or a description in the Write tab.',
  loading: 'We are building the preview.',
  failed: 'We could not build the preview. '
    + 'Check your connection, then select Preview again.',
};

function createEditor(textarea) {
  return new EasyMDE({
    element: textarea,
    forceSync: true,
    spellChecker: false,
    nativeSpellcheck: true,
    autoDownloadFontAwesome: false,
    status: false,
    toolbar: TOOLBAR,
    shortcuts: {
      togglePreview: null,
      toggleSideBySide: null,
      toggleFullScreen: null,
    },
  });
}

function labelEditor(editor, textarea) {
  const label = document.querySelector(`label[for="${textarea.id}"]`);
  if (!label) {
    return;
  }
  label.id = label.id || `${textarea.id}_label`;
  editor.codemirror.getInputField().setAttribute('aria-labelledby', label.id);
  label.addEventListener('click', () => editor.codemirror.focus());
}

function showMessage(panel, text) {
  const message = document.createElement('p');
  message.textContent = text;
  panel.replaceChildren(message);
}

function previewRequest(form) {
  const body = new FormData(form);
  const fileInput = form.querySelector('input[type="file"][name="image_file"]');
  const file = fileInput && fileInput.files[0];
  body.delete('image_file');
  body.set('preview', '1');
  if (file) {
    body.set('preview_image', file.name);
  }
  return { body, file };
}

function isEmpty(body, file) {
  const title = (body.get('title') || '').trim();
  const description = (body.get('description') || '').trim();
  return !title && !description && !file;
}

function prepareContent(root, imageUrl) {
  root.querySelectorAll('img').forEach((img) => {
    if (imageUrl && (img.getAttribute('src') || '').includes(PREVIEW_IMAGE_NAME)) {
      img.src = imageUrl;
      if (img.dataset.gifffer) {
        img.dataset.gifffer = imageUrl;
      }
    }
  });
  root.querySelectorAll('a[href]').forEach((link) => {
    if (link.getAttribute('href').startsWith('#')) {
      link.removeAttribute('href');
    } else {
      link.target = '_blank';
      link.rel = 'noopener noreferrer';
    }
  });
}

function createPreviewLoader(form, panel) {
  let imageUrl = null;
  let latest = 0;

  return async function loadPreview() {
    latest += 1;
    const current = latest;
    if (imageUrl) {
      URL.revokeObjectURL(imageUrl);
      imageUrl = null;
    }

    const { body, file } = previewRequest(form);
    if (isEmpty(body, file)) {
      panel.removeAttribute('aria-busy');
      showMessage(panel, MESSAGES.empty);
      return;
    }

    showMessage(panel, MESSAGES.loading);
    panel.setAttribute('aria-busy', 'true');
    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body,
        redirect: 'error',
      });
      if (!response.ok) {
        throw new Error(`Preview failed with status ${response.status}`);
      }
      const html = await response.text();
      if (current !== latest) {
        return;
      }
      const template = document.createElement('template');
      template.innerHTML = DOMPurify.sanitize(html, PURIFY_OPTIONS);
      if (file) {
        imageUrl = URL.createObjectURL(file);
      }
      prepareContent(template.content, imageUrl);
      panel.replaceChildren(template.content);
    } catch (error) {
      if (current === latest) {
        showMessage(panel, MESSAGES.failed);
      }
    } finally {
      if (current === latest) {
        panel.removeAttribute('aria-busy');
      }
    }
  };
}

function setupTabs(tabs, onSelect) {
  const tabLinks = Array.from(tabs.querySelectorAll('[role="tab"]'));
  const panelOf = (tab) => document.getElementById(tab.getAttribute('aria-controls'));

  tabLinks.forEach((tab) => {
    const panel = panelOf(tab);
    panel.setAttribute('role', 'tabpanel');
    panel.setAttribute('aria-labelledby', tab.id);
  });

  function select(tab) {
    tabLinks.forEach((other) => {
      const active = other === tab;
      other.classList.toggle('is-active', active);
      other.setAttribute('aria-selected', String(active));
      other.tabIndex = active ? 0 : -1;
      panelOf(other).classList.toggle('is-hidden', !active);
    });
    onSelect(tab);
  }

  tabLinks.forEach((tab, index) => {
    tab.addEventListener('click', () => select(tab));
    tab.addEventListener('keydown', (event) => {
      let next = null;
      if (event.key === 'ArrowRight') {
        next = tabLinks[(index + 1) % tabLinks.length];
      } else if (event.key === 'ArrowLeft') {
        next = tabLinks[(index - 1 + tabLinks.length) % tabLinks.length];
      } else if (event.key === 'Home') {
        next = tabLinks[0];
      } else if (event.key === 'End') {
        next = tabLinks[tabLinks.length - 1];
      } else if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        select(tab);
        return;
      }
      if (next) {
        event.preventDefault();
        next.focus();
      }
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const textarea = document.getElementById('id_description');
  const tabs = document.querySelector('[data-entry-tabs]');
  const previewPanel = document.getElementById('entry-preview-panel');
  if (!textarea || !tabs || !previewPanel) {
    return;
  }
  const editor = createEditor(textarea);
  labelEditor(editor, textarea);
  const loadPreview = createPreviewLoader(textarea.form, previewPanel);
  previewPanel.tabIndex = 0;
  setupTabs(tabs, (tab) => {
    if (tab.id === 'entry-tab-preview') {
      loadPreview();
    } else {
      editor.codemirror.refresh();
    }
  });
  tabs.classList.remove('is-hidden');
});
