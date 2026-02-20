var ControlPanelController;

ControlPanelController = class ControlPanelController {
  /*
   * Storage Control Panel controller.
   *
   * Handles the dynamic result field in the Retention Rules DataGrid:
   * when a service is selected from the dropdown, the plain text input
   * for the "Result" column is replaced with an appropriate HTML element
   * based on the service's ResultType (fetched via senaite.jsonapi):
   *
   *   - select, multiselect, multiselect_duplicates, multichoice:
   *     <select> dropdown populated from ResultOptions.
   *   - date:  <input type="date">
   *   - datetime:  <input type="datetime-local">
   *   - numeric, string, text:  <input type="text"> (kept as-is).
   *
   * For multiselect types the stored result is a JSON array; the dropdown
   * still offers a single value per rule — the matching logic in api.py
   * checks membership.
   *
   * On deselect the text input is always restored.
   *
   * Activated only on the storage control panel page
   * (body class ``template-storage-controlpanel``).
   */

  constructor() {
    this.bind_eventhandler = this.bind_eventhandler.bind(this);
    this.on_service_change = this.on_service_change.bind(this);
    this.fetch_and_update_result_field = this.fetch_and_update_result_field.bind(this);
    this.update_result_field = this.update_result_field.bind(this);
    this.replace_with_select = this.replace_with_select.bind(this);
    this.replace_with_date_input = this.replace_with_date_input.bind(this);
    this.replace_with_datetime_input = this.replace_with_datetime_input.bind(this);
    this.restore_text_input = this.restore_text_input.bind(this);
    this.get_result_field = this.get_result_field.bind(this);
    this.get_service_field = this.get_service_field.bind(this);
    this.mark_processed = this.mark_processed.bind(this);
    this.normalize_single_value = this.normalize_single_value.bind(this);
    this.get_portal_url = this.get_portal_url.bind(this);
    this.init_existing_rows = this.init_existing_rows.bind(this);
    this.re_init_rows = this.re_init_rows.bind(this);
    this.debug = this.debug.bind(this);

    // Debounced version used for ajaxStop — waits for the AJAX storm to
    // settle before re-scanning rows, preventing multiple redundant fetches.
    this._re_init_debounced = this._debounce(this.re_init_rows, 300);

    console.debug("ControlPanelController::init");
    this.bind_eventhandler();
    this.init_existing_rows();
    return this;
  }

  bind_eventhandler() {
    this.debug("ControlPanelController::bind_eventhandler");
    // Listen for changes on the service <select> dropdown.
    // The service field is now a plain schema.Choice rendered as <select>.
    $("body").on(
      "change",
      "select[name*='retention_period_rules'][name$='.widgets.service:list']",
      this.on_service_change
    );
    // Re-scan rows after AJAX storms settle.  editform.js has a
    // MutationObserver (childList: true) that can replace DataGrid HTML
    // via update_form(), destroying any custom element we created.
    $(document).on("ajaxStop", this._re_init_debounced);
  }

  on_service_change(event) {
    /*
     * The service dropdown value changed.  If a service UID is selected,
     * fetch its ResultType and update the result field.  If cleared,
     * restore the result field to a plain text input.
     */
    this.debug("ControlPanelController::on_service_change");
    var select = $(event.currentTarget);
    var uid = select.val();
    var row = select.closest("tr");
    if (!row.length) return;

    if (!uid) {
      this.restore_text_input(row);
      return;
    }

    this.restore_text_input(row);
    var result_field = this.get_result_field(row);
    var current_value = result_field.val() || "";
    this.fetch_and_update_result_field(uid, row, current_value);
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
      // Guard: the row may have been removed/replaced while our GET was
      // in-flight.  re_init_rows (via ajaxStop) will catch it.
      if (!row.length || !$.contains(document, row[0])) {
        me.debug("fetch_and_update_result_field: row no longer in DOM, skipping");
        return;
      }
      var result_type = data.ResultType || "numeric";
      var raw_options = data.ResultOptions || [];
      var options = raw_options.map(function(opt) {
        return {value: opt.ResultValue, text: opt.ResultText};
      });
      me.update_result_field(row, result_type, options, current_value);
    }).fail(function() {
      console.warn("[senaite.storage] Failed to fetch service result info");
    });
  }

  update_result_field(row, result_type, options, current_value) {
    /*
     * Dispatch to the correct rendering method based on ResultType.
     */
    this.debug("ControlPanelController::update_result_field:type=" + result_type);
    var option_types = [
      "select", "multiselect", "multiselect_duplicates", "multichoice"
    ];
    if (option_types.indexOf(result_type) !== -1 && options.length) {
      this.replace_with_select(row, options, current_value);
    } else if (result_type === "date") {
      this.replace_with_date_input(row, current_value);
    } else if (result_type === "datetime") {
      this.replace_with_datetime_input(row, current_value);
    } else {
      // numeric, string, text — keep as plain text input
      this.mark_processed(row);
    }
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
     * Replace the result field with a <select> dropdown.
     */
    var field = this.get_result_field(row);
    if (!field.length) return;

    // Normalise: multiselect results are JSON arrays; extract single value
    var select_value = this.normalize_single_value(current_value);

    // Already a select? Just update the value
    if (field.prop("tagName") === "SELECT") {
      field.val(select_value);
      this.mark_processed(row);
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
    this.mark_processed(row);
  }

  replace_with_date_input(row, current_value) {
    /*
     * Turn the result field into an <input type="date">.
     *
     * Changes the type attribute in-place rather than replacing the DOM
     * node.  editform.js has a MutationObserver (childList: true,
     * attributes: false) — an in-place attribute change is invisible to
     * it, avoiding the notify_added → ajaxStop cascade that would
     * otherwise corrupt the DataGrid row numbering.
     */
    var field = this.get_result_field(row);
    if (!field.length) return;

    // For a <select> (row was previously a select-type service),
    // we must replace the element since we can't convert tags.
    if (field.prop("tagName") === "SELECT") {
      var input = $("<input>", {
        type: "date",
        name: field.attr("name"),
        id: field.attr("id"),
        "class": field.attr("class"),
        value: current_value,
      });
      field.replaceWith(input);
      this.mark_processed(row);
      return;
    }

    // In-place: just change the type attribute (no childList mutation)
    field.attr("type", "date");
    field.val(current_value);
    this.mark_processed(row);
  }

  replace_with_datetime_input(row, current_value) {
    /*
     * Turn the result field into an <input type="datetime-local">.
     *
     * Same in-place strategy as replace_with_date_input — see its
     * docstring for rationale.
     */
    var field = this.get_result_field(row);
    if (!field.length) return;

    if (field.prop("tagName") === "SELECT") {
      var input = $("<input>", {
        type: "datetime-local",
        name: field.attr("name"),
        id: field.attr("id"),
        "class": field.attr("class"),
        value: current_value,
      });
      field.replaceWith(input);
      this.mark_processed(row);
      return;
    }

    field.attr("type", "datetime-local");
    field.val(current_value);
    this.mark_processed(row);
  }

  restore_text_input(row) {
    /*
     * Restore the result field back to a plain text input.
     *
     * For <input> fields (date, datetime-local, text) the type attribute
     * is changed in-place to avoid MutationObserver side-effects.
     * For <select> elements a replacement is unavoidable.
     */
    var field = this.get_result_field(row);
    if (!field.length) return;

    if (field.prop("tagName") === "INPUT") {
      // In-place: change type back to text (no childList mutation)
      field.attr("type", "text");
      field.val("");
      field.removeAttr("data-storage-processed");
      return;
    }

    // <select> → must replace with a new <input>
    var input = $("<input>", {
      type: "text",
      name: field.attr("name"),
      id: field.attr("id"),
      "class": field.attr("class"),
      value: "",
    });
    field.replaceWith(input);
  }

  get_result_field(row) {
    /*
     * Find the result field in a DataGrid row (any element type).
     */
    return row.find(
      "input[name$='.widgets.result'], select[name$='.widgets.result']"
    );
  }

  get_service_field(row) {
    /*
     * Find the service <select> in a DataGrid row.
     */
    return row.find("select[name$='.widgets.service:list']");
  }

  mark_processed(row) {
    /*
     * Mark a row's result field as processed so re_init_rows skips it.
     *
     * The attribute is set on the result field itself, so it is
     * automatically lost when editform.js replaces the DataGrid HTML,
     * which is exactly when we need to re-process.
     */
    var field = this.get_result_field(row);
    field.attr("data-storage-processed", "true");
  }

  init_existing_rows() {
    /*
     * On page load, initialise rows that already have a service selected.
     */
    this.debug("ControlPanelController::init_existing_rows");
    this.re_init_rows();
  }

  re_init_rows() {
    /*
     * Re-initialise rows that have a service selected but whose result
     * field has not yet been processed.
     *
     * Called on page load and (debounced) on every ajaxStop so that DOM
     * replacements made by editform.js's update_form() are repaired.
     * Rows whose result field carries the data-storage-processed
     * attribute are skipped, which naturally terminates any potential
     * loop: once a row is processed the next ajaxStop invocation does
     * nothing for it.
     */
    this.debug("ControlPanelController::re_init_rows");
    var me = this;
    $("select[name*='retention_period_rules'][name$='.widgets.service:list']")
      .each(function() {
        var uid = $(this).val();
        if (!uid) return;
        var row = $(this).closest("tr");
        if (!row.length) return;
        // Skip rows already processed
        var field = me.get_result_field(row);
        if (!field.length) return;
        if (field.attr("data-storage-processed")) return;
        me.fetch_and_update_result_field(uid, row, field.val() || "");
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
