
$(function () {

  // Get URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const readyString = urlParams.get('ready');
  let ready = '';
  if (readyString) {
    ready = urlParams.get('ready').toLowerCase() === 'true';
  }
  ready = ready ? 'True' : 'False';

  // Get the URL from a data attribute in the table
  const dataTable = $('#dataTable');
  const ajaxUrl = dataTable.data('ajax-url'); // Fetch the URL from a data attribute

  // Initialize DataTables
  dataTable.DataTable({
    processing: true,
    serverSide: true,
    length: 100,
    pageLength: 100,
    order: [[0, 'asc']],
    ajax: `${ajaxUrl}?approved=${dataTable.data('approved')}&ready=${ready}`,
    columnDefs: [
      { bSortable: false, aTargets: [1, 2] },
      {
        targets: [1, 2],
      },
    ],
  });
});