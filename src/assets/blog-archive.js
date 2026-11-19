// All post links and metadata are in the static HTML. Enhance each mounted archive
// independently so React Router visits and ordinary page loads behave alike.
class PostArchive extends HTMLElement {
  connectedCallback() {
    this.frame = requestAnimationFrame(() => {
      const search = this.querySelector('input[type="search"]');
      const clearSearch = this.querySelector('[data-clear-search]');
      const choices = [...this.querySelectorAll('[data-filter]')];
      const posts = [...this.querySelectorAll('[data-search]')];
      const status = this.querySelector('[role="status"]');
      const current = new URL(window.location.href);
      search.value = current.searchParams.get('q') || '';
      let kind = current.searchParams.get('type') || '';
      if (!choices.some(button => button.dataset.filter === kind)) kind = '';

      const update = () => {
        const terms = search.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
        let shown = 0;
        for (const post of posts) {
          const text = post.dataset.search.toLowerCase();
          post.hidden = (kind && post.dataset.kind !== kind) || !terms.every(term => text.includes(term));
          if (!post.hidden) shown++;
        }
        for (const button of choices) {
          button.setAttribute('aria-pressed', String(button.dataset.filter === kind));
        }
        clearSearch.hidden = shown > 0 || terms.length === 0;
        status.textContent = !kind && !terms.length ? '' : shown
          ? `${shown} ${shown === 1 ? 'post' : 'posts'}`
          : 'No posts found.';
      };

      const save = () => {
        const url = new URL(window.location.href);
        if (kind) url.searchParams.set('type', kind);
        else url.searchParams.delete('type');
        if (search.value.trim()) url.searchParams.set('q', search.value.trim());
        else url.searchParams.delete('q');
        window.history.replaceState(window.history.state, '', url);
        update();
      };

      this.events = new AbortController();
      const options = { signal: this.events.signal };
      search.addEventListener('input', save, options);
      clearSearch.addEventListener('click', () => {
        search.value = '';
        save();
        search.focus();
      }, options);
      for (const button of choices) {
        button.addEventListener('click', () => {
          kind = button.dataset.filter;
          save();
        }, options);
      }
      update();
    });
  }

  disconnectedCallback() {
    cancelAnimationFrame(this.frame);
    this.events?.abort();
  }
}

if (!customElements.get('post-archive')) customElements.define('post-archive', PostArchive);
