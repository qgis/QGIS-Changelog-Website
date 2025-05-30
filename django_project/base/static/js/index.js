require("../style/scss/style.scss");

import 'datatables.net';
import 'datatables.net-dt';
import 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'air-datepicker';
import 'air-datepicker/air-datepicker.css';
import 'air-datepicker/locale/en';
import 'jquery-ui/ui/widgets/sortable';
import 'jquery-ui/themes/base/sortable.css';

document.addEventListener("DOMContentLoaded", () => {
  // Get all "navbar-burger" elements
  const $navbarBurgers = Array.prototype.slice.call(
    document.querySelectorAll(".navbar-burger"),
    0
  );

  // Add a click event on each of them
  $navbarBurgers.forEach((el) => {
    el.addEventListener("click", () => {
      // Get the target from the "data-target" attribute
      const target = el.dataset.target;
      const $target = document.getElementById(target);

      // Toggle the "is-active" class on both the "navbar-burger" and the "navbar-menu"
      el.classList.toggle("is-active");
      $target.classList.toggle("is-active");
    });
  });
});
