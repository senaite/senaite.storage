var ControlPanelController;

ControlPanelController = class ControlPanelController {
  /*
   * Storage Control Panel controller.
   *
   * Handles the dynamic result field in the Retention Rules DataGrid:
   * when a service with predefined result options is selected, the plain
   * text input for the "Result" column is replaced with a <select>
   * dropdown populated from the service's ResultOptions (fetched via
   * senaite.jsonapi).  On deselect the text input is restored.
   *
   * Works for all result types that carry ResultOptions (select,
   * multiselect, multiselect_duplicates, multichoice).  For multiselect
   * types the stored result is a JSON array; the dropdown still offers a
   * single value per rule — the matching logic in api.py checks membership.
   *
   * Activated only on the storage control panel page
   * (body class ``template-storage-controlpanel``).
   */

  constructor() {
    this.bind_eventhandler = this.bind_eventhandler.bind(this);
    this.on_service_select = this.on_service_select.bind(this);
    this.on_service_deselect = this.on_service_deselect.bind(this);
    this.fetch_and_update_result_field = this.fetch_and_update_result_field.bind(this);
    this.replace_with_select = this.replace_with_select.bind(this);
    this.restore_text_input = this.restore_text_input.bind(this);
    this.normalize_single_value = this.normalize_single_value.bind(this);
    this.get_portal_url = this.get_portal_url.bind(this);
    this.init_existing_rows = this.init_existing_rows.bind(this);
    this.re_init_rows = this.re_init_rows.bind(this);
    this.debug = this.debug.bind(this);

    // Debounced version used for ajaxStop — waits for the AJAX storm to
    // settle (ajax_form/modified, ajax_form/added, our own GETs) before
    // re-scanning rows, preventing multiple redundant fetches.
    this._re_init_debounced = this._debounce(this.re_init_rows, 300);

    console.debug("ControlPanelController::init");
    this.bind_eventhandler();
    this.init_existing_rows();
    return this;
  }

  bind_eventhandler() {
    this.debug("ControlPanelController::bind_eventhandler");
    $("body").on(
      "select",
      "textarea[name*='retention_period_rules'][name$='.widgets.service']",
      this.on_service_select
    );
    $("body").on(
      "deselect",
      "textarea[name*='retention_period_rules'][name$='.widgets.service']",
      this.on_service_deselect
    );
    // Re-scan rows after every AJAX storm settles.
    //
    // senaite.core's editform.js hooks the same UIDReferenceWidget select/
    // deselect events and sends ajax_form/modified and ajax_form/added POSTs.
    // The update_form() handler can replace DataGrid HTML, which destroys
    // any <select> we just created.  Listening to ajaxStop (debounced) lets
    // us restore the <select> after the dust settles, without introducing an
    // infinite loop: re_init_rows only acts on rows that still have a plain
    // text input — once converted to <select> they are left untouched.
    $(document).on("ajaxStop", this._re_init_debounced);
  }

  on_service_select(event) {
    /*
     * A service was selected in a DataGrid row. Fetch the service's
     * ResultOptions and replace the result text input with a <select>.
     */
    this.debug("ControlPanelController::on_service_select");
    var uid = event.detail && event.detail.value;
    if (!uid) return;

    var row = $(event.currentTarget).closest("tr");
    if (!row.length) return;

    var result_field = row.find(
      "input[name$='.widgets.result'], select[name$='.widgets.result']"
    );
    var current_value = result_field.val() || "";
    this.fetch_and_update_result_field(uid, row, current_value);
  }

  on_service_deselect(event) {
    /*
     * A service was deselected. Restore the result field to a text input.
     */
    this.debug("ControlPanelController::on_service_deselect");
    var row = $(event.currentTarget).closest("tr");
    if (!row.length) return;
    this.restore_text_input(row);
  }

  fetch_and_update_result_field(uid, row, current_value) {
    /*
     * Fetch service data from senaite.jsonapi and update the result field.
     *
     * The UID route (@@API/senaite/v1/{uid}) returns the full record with
     * complete=True by default, including ResultType and ResultOptions.
     */
    this.debug("ControlPanelController::fetch_and_update_result_field:uid=" + uid);
    var url = this.get_portal_url() + "/@@API/senaite/v1/" + uid;
    var me = this;
    $.ajax({
      url: url,
      type: "GET",
      dataType: "json",
      context: this,
    }).done(function(data) {
      // Guard: the row may have been removed/replaced by update_form() while
      // our GET was in-flight.  re_init_rows (via ajaxStop) will catch it.
      if (!row.length || !$.contains(document, row[0])) {
        me.debug("fetch_and_update_result_field: row no longer in DOM, skipping");
        return;
      }
      var raw_options = data.ResultOptions || [];
      var options = raw_options.map(function(opt) {
        return {value: opt.ResultValue, text: opt.ResultText};
      });
      if (!options.length) {
        me.restore_text_input(row);
        return;
      }
      me.replace_with_select(row, options, current_value);
    }).fail(function() {
      console.warn("[senaite.storage] Failed to fetch service result info");
    });
  }

  normalize_single_value(value) {
    /*
     * Extract a single string from a value that may be a JSON array.
     *
     * Multiselect/multichoice analyses store their result as a JSON array
     * like '["1"]'.  Retention rules always match on a single value, so
     * we extract the first element when an array is present.
     */
    if (!value || value.charAt(0) !== "[") return value || "";
    try {
      var parsed = JSON.parse(value);
      return Array.isArray(parsed) && parsed.length ? String(parsed[0]) : "";
    } catch (e) {
      return "";
    }
  }

  replace_with_select(row, options, current_value) {
    /*
     * Replace the result text input with a <select> dropdown.
     */
    var field = row.find(
      "input[name$='.widgets.result'], select[name$='.widgets.result']"
    );
    if (!field.length) return;

    // Normalise: multiselect results are JSON arrays; extract single value
    var select_value = this.normalize_single_value(current_value);

    // Already a select? Just update the value
    if (field.prop("tagName") === "SELECT") {
      field.val(select_value);
      return;
    }

    var select = $("<select>", {
      name: field.attr("name"),
      id: field.attr("id"),
      class: field.attr("class"),
    });

    select.append($("<option>", {value: "", text: "-- Any result --"}));
    $.each(options, function(i, opt) {
      select.append($("<option>", {
        value: opt.value,
        text: opt.text,
        selected: opt.value === select_value,
      }));
    });

    field.replaceWith(select);
  }

  restore_text_input(row) {
    /*
     * Restore the result field back to a plain text input.
     */
    var select = row.find("select[name$='.widgets.result']");
    if (!select.length) return;

    var input = $("<input>", {
      type: "text",
      name: select.attr("name"),
      id: select.attr("id"),
      class: select.attr("class"),
      value: "",
    });
    select.replaceWith(input);
  }

  init_existing_rows() {
    /*
     * On page load, initialise rows that already have a service selected.
     * Trigger a synthetic select event so the handler replaces the input.
     */
    this.debug("ControlPanelController::init_existing_rows");
    $("textarea[name*='retention_period_rules'][name$='.widgets.service']")
      .each(function() {
        var uid = $(this).val().trim();
        if (!uid) return;
        $(this).trigger({
          type: "select",
          detail: {value: uid},
        });
      });
  }

  re_init_rows() {
    /*
     * Re-initialise rows that have a service selected but whose result
     * field is still a plain text input.
     *
     * Called (debounced) on every ajaxStop so that DOM replacements made
     * by editform.js's update_form() are repaired.  Rows already showing
     * a <select> are skipped, which naturally terminates any potential
     * loop: once a row is converted the next ajaxStop invocation does
     * nothing for it.
     */
    this.debug("ControlPanelController::re_init_rows");
    var me = this;
    $("textarea[name*='retention_period_rules'][name$='.widgets.service']")
      .each(function() {
        var uid = $(this).val().trim();
        if (!uid) return;
        var row = $(this).closest("tr");
        if (!row.length) return;
        // Only act when the result field is still a plain text input.
        var input = row.find("input[name$='.widgets.result']");
        if (!input.length) return;
        me.fetch_and_update_result_field(uid, row, input.val() || "");
      });
  }

  _debounce(fn, delay) {
    /*
     * Return a debounced wrapper of fn that fires after delay ms of
     * inactivity.
     */
    var timer = null;
    var me = this;
    return function() {
      clearTimeout(timer);
      timer = setTimeout(function() { fn.call(me); }, delay);
    };
  }

  get_portal_url() {
    /*
     * Return the portal URL
     */
    var url = $("input[name=portal_url]").val();
    return url || window.portal_url;
  }

  debug(message) {
    return console.debug("[senaite.storage] " + message);
  }

};

export default ControlPanelController;
