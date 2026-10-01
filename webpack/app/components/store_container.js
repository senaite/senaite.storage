var StoreContainerController;

StoreContainerController = class StoreContainerController {
  /*
   * Store Samples in a Container view controller
   */
  constructor() {
    this.bind_eventhandler = this.bind_eventhandler.bind(this);
    this.on_position_change = this.on_position_change.bind(this);
    this.on_position_slot_click = this.on_position_slot_click.bind(this);
    this.on_sample_select = this.on_sample_select.bind(this);
    this.fetch_default_retention_period = this.fetch_default_retention_period.bind(this);
    this.get_portal_url = this.get_portal_url.bind(this);
    this.debug = this.debug.bind(this);
    console.debug("StoreContainerController::init");
    // bind the event handler to the elements
    this.bind_eventhandler();
    if ($("#position").length) {
      $("#position").change();
    }
    return this;
  }

  bind_eventhandler() {
    this.debug("StoreContainerController::bind_eventhandler");
    $("body").on("click", "a.position_slot_selector", this.on_position_slot_click);
    $("body").on("change", "#position", this.on_position_change);
    $("body").on("select", ".senaite-uidreference-widget-input textarea", this.on_sample_select);
    return $("body").on("deselect", ".senaite-uidreference-widget-input textarea", this.on_sample_select);
  }

  on_position_change(event) {
    var select;
    /*
     * The selected value from the position selected list has changed. Make the
     * counterpart position selector from the layout more visible
     */
    this.debug("StoreContainerController::on_position_change");
    select = $(event.currentTarget);
    $("td.empty-slot").removeClass("selected");
    if (!select.val()) {
      return;
    }
    return $("#" + select.val()).parent("td.empty-slot").addClass("selected");
  }

  on_position_slot_click(event) {
    var anchor, sample_uid, select;
    /*
     * The user has clicked to a position slot from the layout. Update the
     * value for position selection list and submit
     */
    this.debug("StoreContainerController::on_position_slot_click");
    event.preventDefault();
    if (!$("#position").length) {
      return;
    }
    anchor = $(event.currentTarget);
    select = $("#position").val(anchor.attr("id"));
    $("#position").change();
    sample_uid = $("#sample_uid").val();
    if (sample_uid) {
      return $("#button_store").click();
    }
  }

  on_sample_select(event) {
    /*
     * When a sample is selected, fetch the default retention period
     * and populate the retention period input field
     */
    this.debug("StoreContainerController::on_sample_select");
    var sample_uid = event.detail ? event.detail.value : "";
    if (sample_uid) {
      this.fetch_default_retention_period(sample_uid);
    } else {
      $("#retention_period").val("");
    }
  }

  fetch_default_retention_period(sample_uid) {
    /*
     * Fetch the default retention period for a sample via the JSON API
     */
    var method_name = "getDefaultStorageRetentionPeriod";
    this.debug("StoreContainerController::fetch_default_retention_period:sample_uid=" + sample_uid);
    $.ajax({
      url: this.get_portal_url() + "/@@API/read",
      type: "POST",
      context: this,
      dataType: "json",
      data: {
        catalog_name: "uid_catalog",
        UID: sample_uid,
        include_fields: [],
        include_methods: [method_name],
      }
    }).done(function(data) {
      var days = data.objects[0][method_name];
      if (days !== null && days !== undefined) {
        $("#retention_period").val(days);
      } else {
        $("#retention_period").val("");
      }
    }).fail(function() {
      console.warn("Failed to get default retention period");
    });
  }

  get_portal_url() {
    /*
     * Return the portal url (calculated in code)
     */
    var url;
    url = $("input[name=portal_url]").val();
    return url || window.portal_url;
  }

  debug(message) {
    return console.debug("[senaite.storage] " + message);
  }

};

export default StoreContainerController;
