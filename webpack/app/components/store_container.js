
/* Please use this command to compile this file into the proper folder:
    coffee --no-header -w -o ../ -c store_container.coffee
 */
var StoreContainerController,
  bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

StoreContainerController = (function() {

  /*
   * Store Samples in a Container view controller
   */
  function StoreContainerController() {
    this.debug = bind(this.debug, this);
    this.on_position_slot_click = bind(this.on_position_slot_click, this);
    this.on_position_change = bind(this.on_position_change, this);
    this.bind_eventhandler = bind(this.bind_eventhandler, this);
    console.debug("StoreContainerController::init");
    this.bind_eventhandler();
    $("#position").change();
    return this;
  }

  StoreContainerController.prototype.bind_eventhandler = function() {
    this.debug("StoreContainerController::bind_eventhandler");
    $("body").on("click", "a.position_slot_selector", this.on_position_slot_click);
    return $("body").on("change", "#position", this.on_position_change);
  };

  StoreContainerController.prototype.on_position_change = function(event) {

    /*
     * The selected value from the position selected list has changed. Make the
     * counterpart position selector from the layout more visible
     */
    var select;
    this.debug("StoreContainerController::on_position_change");
    select = $(event.currentTarget);
    $("td.empty-slot").removeClass("selected");
    return $("#" + select.val()).parent("td.empty-slot").addClass("selected");
  };

  StoreContainerController.prototype.on_position_slot_click = function(event) {

    /*
     * The user has clicked to a position slot from the layout. Update the
     * value for position selection list and submit
     */
    var anchor, sample_uid, select;
    this.debug("StoreContainerController::on_position_slot_click");
    event.preventDefault();
    anchor = $(event.currentTarget);
    select = $("#position").val(anchor.attr("id"));
    $("#position").change();
    sample_uid = $("#sample_uid").val();
    if (sample_uid) {
      return $("#button_store").click();
    }
  };

  StoreContainerController.prototype.debug = function(message) {
    return console.debug("[senaite.storage] " + message);
  };

  return StoreContainerController;

})();

export default StoreContainerController;
