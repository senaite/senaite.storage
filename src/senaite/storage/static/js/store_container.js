(function() {
  /* Please use this command to compile this file into the proper folder:
      coffee --no-header -w -o ../ -c store_container.coffee
  */
  // DOCUMENT READY ENTRY POINT
  document.addEventListener("DOMContentLoaded", function() {
    console.debug("[senaite.storage] DOMContentLoaded: --> Loading Store Container Controller");
    return window.store_container_controller = new StoreContainerController;
  });

  window.StoreContainerController = class StoreContainerController {
    /*
     * Store Samples in a Container view controller
     */
    constructor() {
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      this.on_position_change = this.on_position_change.bind(this);
      this.on_position_slot_click = this.on_position_slot_click.bind(this);
      this.debug = this.debug.bind(this);
      // bind the event handler to the elements
      this.bind_eventhandler();
      $("#position").change();
      return this;
    }

    bind_eventhandler() {
      this.debug("StoreContainerController::bind_eventhandler");
      $("body").on("click", "a.position_slot_selector", this.on_position_slot_click);
      return $("body").on("change", "#position", this.on_position_change);
    }

    on_position_change(event) {
      /*
       * The selected value from the position selected list has changed. Make the
       * counterpart position selector from the layout more visible
       */
      var select;
      select = $(event.currentTarget);
      $("td.empty-slot").removeClass("selected");
      return $("#" + select.val()).parent("td.empty-slot").addClass("selected");
    }

    on_position_slot_click(event) {
      var anchor, sample_uid, select;
      /*
       * The user has clicked to a position slot from the layout. Update the
       * value for position selection list and submit
       */
      event.preventDefault();
      anchor = $(event.currentTarget);
      select = $("#position").val(anchor.attr("id"));
      $("#position").change();
      sample_uid = $("#sample_uid").val();
      if (sample_uid) {
        return $("#button_store").click();
      }
    }

    debug(message) {
      return console.debug("[senaite.storage] " + message);
    }

  };

}).call(this);
