### Please use this command to compile this file into the proper folder:
    coffee --no-header -w -o ../ -c store_samples.coffee
###

# DOCUMENT READY ENTRY POINT
document.addEventListener "DOMContentLoaded", ->
  console.debug "[senaite.storage] DOMContentLoaded: --> Loading Store Samples Controller"
  window.store_samples_controller = new StoreSamplesController

class window.StoreSamplesController
  ###
   * Store Samples view controller
  ###

  constructor: ->
    # bind the event handler to the elements
    @bind_eventhandler()
    return @

  bind_eventhandler: =>
    @debug "StoreSamplesController::bind_eventhandler"
    $("body").on "selected", ".ArchetypesReferenceWidget input", @on_container_change
    $("body").on "change", "select[name='samples\\.container_position:records']", @on_container_position_change

  on_container_change: (event) =>
    ###
     * Fills the select element next to the container input with the positions
     * that are available for storage
    ###
    $container = $(event.currentTarget)
    container_uid = $container.attr "uid"
    sample_uid = $container.attr "sample_uid"
    select = $("#container_position\\."+sample_uid+"_uid")[0]
    @fill_container_positions(container_uid, select)
    return

  on_container_position_change: (event) =>
    ###
     * Purges the positions from other select elements that are bounded to
     * same container. This ensures that a given position within a container can
     * only be selected once
    ###
    select = $(event.currentTarget)
    container_uid = select.attr "container_uid"
    if not container_uid
        return
    position = select.val()
    @purge_container_position(container_uid, position)
    orig_value = select.attr "original_value"
    $(select).attr "original_value", position
    if not orig_value
        return
    @add_container_position(container_uid, orig_value)

  add_container_position: (container_uid, position) =>
    ###
     * Adds the option for the specified position to all select elements that
     * are bound to the container passed in that do not contain this position
     * already
    ###
    selects = @get_container_position_selects(container_uid)
    $.each selects, (index, select) ->
      options = $(select).find("option")
      positions = $(options).map () ->
        $(this).val()
      positions = $.makeArray(positions)
      if positions.indexOf(position) >= 0
        return
      positions.push position
      positions.sort()
      orig_value = $(select).val()
      $(select).find("option").remove()
      $.each positions, (index, new_position) ->
        $(select).append(new Option(new_position, new_position))
      $(select).val(orig_value)
    return

  purge_container_position: (container_uid, position) =>
    ###
     * Removes the option for the specified position from all select elements
     * that are bound to the container passed in. It only affects to those
     * elements that have a position selected other than the one passed in.
    ###
    selects = @get_container_position_selects(container_uid)
    $.each selects, (index, select) ->
      if $(select).val() != position
        $(select).find("option[value='"+position+"']").remove()
    return

  get_container_position_selects: (container_uid) =>
    ###
     * Returns all DOM select elements for layout position selection that are
     * bound to the container passed in
    ###
    selects_name = "samples\\.container_position:records"
    $("select[name='"+selects_name+"'][container_uid='"+container_uid+"']")

  fill_container_positions: (container_uid, select) =>
    ###
     * Populates the select DOM element with options that are the positions
     * the container has available for storage. The first option is set as the
     * default value for the select element and the rest of select elements for
     * same container are updated accordingly to prevent same position to be
     * assigned twice
    ###
    $(select).find("option").remove()
    $(select).attr "original_value", ""
    $(select).attr "container_uid", container_uid
    @fetch_available_positions container_uid
    .done (positions) ->
      selected_positions = @get_selected_positions(container_uid)
      available = @diff(positions, $.makeArray(selected_positions))
      for position in available
        $(select).append(new Option(position, position))
      $(select).val(available[0])
      $(select).trigger "change"
      return
    .fail ->
      console.warn "Failed to get available positions"
      return
    return

  diff: (a1, a2) =>
    ###
     * Returns the difference (intersection) between two arrays
    ###
    a1.concat(a2)
    .filter (val, index, arr) ->
      arr.indexOf(val) == arr.lastIndexOf(val)

  get_selected_positions: (container_uid) =>
    ###
     * Return the positions that are currently selected in the form for a given
     * container
    ###
    selects = @get_container_position_selects(container_uid)
    $(selects)
    .map () ->
      $(this).val()

  fetch_available_positions: (uid) =>
    ###
     * Returns the available positions from a sample container with the uid
     * passed in. If no container found for this uid, returns null
    ###
    deferred = $.Deferred()
    field_name = "AvailablePositions"
    @ajax_submit
      url: @get_portal_url() + "/@@API/read"
      data:
        catalog_name: "uid_catalog"
        UID: uid
        include_fields: [field_name]
    .done (data) ->
      return deferred.resolveWith this, [data.objects[0][field_name]]
    return deferred.promise()

  ajax_submit: (options) =>
    options ?= {}
    options.type ?= "POST"
    options.url ?= @get_portal_url()
    options.context ?= this
    options.dataType ?= "json"
    options.data ?= {}

    @debug "ajax_submit::options=", options

    $(this).trigger "ajax:submit:start"
    done = ->
      $(this).trigger "ajax:submit:end"
    return $.ajax(options).done done

  get_portal_url: =>
    ###
     * Return the portal url (calculated in code)
    ###
    url = $("input[name=portal_url]").val()
    return url or window.portal_url

  debug: (message) =>
    console.debug "[senaite.storage] "+message
