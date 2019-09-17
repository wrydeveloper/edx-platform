import { getLearnerPortalLinks } from '@edx/frontend-enterprise';

function CustomUserMenuLinks() {
  const learnerPortalLinks = getLearnerPortalLinks();
  const $dashboardLink = $('#userMenu .dashboard');
  const classNames = 'mobile-nav-item dropdown-item dropdown-nav-item';
  for (let i = 0; i < learnerPortalLinks.length; i += 1) {
    const link = learnerPortalLinks[i];

    $dashboardLink.after(
      `<div class="${classNames}"><a href="${link.url}" role="menuitem">${link.title}</a></div>`
    );
  }
}

export { CustomUserMenuLinks }; // eslint-disable-line import/prefer-default-export
