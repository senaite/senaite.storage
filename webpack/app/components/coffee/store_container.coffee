### Please use this command to compile this file into the proper folder:
    coffee --no-header -w -o ../ -c store_container.coffee
###

class StoreContainerController
  ###
   * Store Samples in a Container view controller
  ###

  constructor: ->
    console.debug "StoreContainerController::init"
    # bind the event handler to the elements
    @bind_eventhandler()
    $("#position").change()
    return @

  bind_eventhandler: =>
    @debug "StoreContainerController::bind_eventhandler"
    $("body").on "click", "a.position_slot_selector", @on_position_slot_click
    $("body").on "change", "#position", @on_position_change

  on_position_change: (event) =>
    ###
     * The selected value from the position selected list has changed. Make the
     * counterpart position selector from the layout more visible
    ###
    @debug "StoreContainerController::on_position_change"
    select = $(event.currentTarget)
    $("td.empty-slot").removeClass("selected")
    $("#"+select.val()).parent("td.empty-slot").addClass("selected")

  on_position_slot_click: (event) =>
    ###
     * The user has clicked to a position slot from the layout. Update the
     * value for position selection list and submit
    ###
    @debug "StoreContainerController::on_position_slot_click"
    event.preventDefault()
    anchor = $(event.currentTarget)
    select = $("#position").val(anchor.attr("id"))
    $("#position").change()
    sample_uid = $("#sample_uid").val()
    if sample_uid
        $("#button_store").click()

  debug: (message) =>
    console.debug "[senaite.storage] "+message

export default StoreContainerController
