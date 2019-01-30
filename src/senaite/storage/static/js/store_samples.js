(function() {
  /* Please use this command to compile this file into the proper folder:
      coffee --no-header -w -o ../ -c store_samples.coffee
  */
  // DOCUMENT READY ENTRY POINT
  document.addEventListener("DOMContentLoaded", function() {
    console.debug("[senaite.storage] DOMContentLoaded: --> Loading Store Samples Controller");
    return window.store_samples_controller = new StoreSamplesController;
  });

  window.StoreSamplesController = class StoreSamplesController {
    /*
     * Store Samples view controller
     */
    constructor() {
      this.bind_eventhandler = this.bind_eventhandler.bind(this);
      this.on_container_change = this.on_container_change.bind(this);
      this.on_container_position_change = this.on_container_position_change.bind(this);
      this.add_container_position = this.add_container_position.bind(this);
      this.purge_container_position = this.purge_container_position.bind(this);
      this.get_container_position_selects = this.get_container_position_selects.bind(this);
      this.fill_container_positions = this.fill_container_positions.bind(this);
      this.diff = this.diff.bind(this);
      this.get_selected_positions = this.get_selected_positions.bind(this);
      this.fetch_available_positions = this.fetch_available_positions.bind(this);
      this.ajax_submit = this.ajax_submit.bind(this);
      this.get_portal_url = this.get_portal_url.bind(this);
      this.debug = this.debug.bind(this);
      // bind the event handler to the elements
      this.bind_eventhandler();
      return this;
    }

    bind_eventhandler() {
      this.debug("StoreSamplesController::bind_eventhandler");
      $("body").on("selected", ".ArchetypesReferenceWidget input", this.on_container_change);
      return $("body").on("change", "select[name='samples\\.container_position:records']", this.on_container_position_change);
    }

    on_container_change(event) {
      /*
       * Fills the select element next to the container input with the positions
       * that are available for storage
       */
      var $container, container_uid, sample_uid, select;
      $container = $(event.currentTarget);
      container_uid = $container.attr("uid");
      sample_uid = $container.attr("sample_uid");
      select = $("#container_position\\." + sample_uid + "_uid")[0];
      this.fill_container_positions(container_uid, select);
    }

    on_container_position_change(event) {
      /*
       * Purges the positions from other select elements that are bounded to
       * same container. This ensures that a given position within a container can
       * only be selected once
       */
      var container_uid, orig_value, position, select;
      select = $(event.currentTarget);
      container_uid = select.attr("container_uid");
      if (!container_uid) {
        return;
      }
      position = select.val();
      this.purge_container_position(container_uid, position);
      orig_value = select.attr("original_value");
      $(select).attr("original_value", position);
      if (!orig_value) {
        return;
      }
      return this.add_container_position(container_uid, orig_value);
    }

    add_container_position(container_uid, position) {
      /*
       * Adds the option for the specified position to all select elements that
       * are bound to the container passed in that do not contain this position
       * already
       */
      var selects;
      selects = this.get_container_position_selects(container_uid);
      $.each(selects, function(index, select) {
        var options, orig_value, positions;
        options = $(select).find("option");
        positions = $(options).map(function() {
          return $(this).val();
        });
        positions = $.makeArray(positions);
        if (positions.indexOf(position) >= 0) {
          return;
        }
        positions.push(position);
        positions.sort();
        orig_value = $(select).val();
        $(select).find("option").remove();
        $.each(positions, function(index, new_position) {
          return $(select).append(new Option(new_position, new_position));
        });
        return $(select).val(orig_value);
      });
    }

    purge_container_position(container_uid, position) {
      /*
       * Removes the option for the specified position from all select elements
       * that are bound to the container passed in. It only affects to those
       * elements that have a position selected other than the one passed in.
       */
      var selects;
      selects = this.get_container_position_selects(container_uid);
      $.each(selects, function(index, select) {
        if ($(select).val() !== position) {
          return $(select).find("option[value='" + position + "']").remove();
        }
      });
    }

    get_container_position_selects(container_uid) {
      /*
       * Returns all DOM select elements for layout position selection that are
       * bound to the container passed in
       */
      var selects_name;
      selects_name = "samples\\.container_position:records";
      return $("select[name='" + selects_name + "'][container_uid='" + container_uid + "']");
    }

    fill_container_positions(container_uid, select) {
      /*
       * Populates the select DOM element with options that are the positions
       * the container has available for storage. The first option is set as the
       * default value for the select element and the rest of select elements for
       * same container are updated accordingly to prevent same position to be
       * assigned twice
       */
      $(select).find("option").remove();
      $(select).attr("original_value", "");
      $(select).attr("container_uid", container_uid);
      this.fetch_available_positions(container_uid).done(function(positions) {
        var available, i, len, position, selected_positions;
        selected_positions = this.get_selected_positions(container_uid);
        available = this.diff(positions, $.makeArray(selected_positions));
        for (i = 0, len = available.length; i < len; i++) {
          position = available[i];
          $(select).append(new Option(position, position));
        }
        $(select).val(available[0]);
        $(select).trigger("change");
      }).fail(function() {
        console.warn("Failed to get available positions");
      });
    }

    diff(a1, a2) {
      /*
       * Returns the difference (intersection) between two arrays
       */
      return a1.concat(a2).filter(function(val, index, arr) {
        return arr.indexOf(val) === arr.lastIndexOf(val);
      });
    }

    get_selected_positions(container_uid) {
      /*
       * Return the positions that are currently selected in the form for a given
       * container
       */
      var selects;
      selects = this.get_container_position_selects(container_uid);
      return $(selects).map(function() {
        return $(this).val();
      });
    }

    fetch_available_positions(uid) {
      /*
       * Returns the available positions from a sample container with the uid
       * passed in. If no container found for this uid, returns null
       */
      var deferred, field_name;
      deferred = $.Deferred();
      field_name = "AvailablePositions";
      this.ajax_submit({
        url: this.get_portal_url() + "/@@API/read",
        data: {
          catalog_name: "uid_catalog",
          UID: uid,
          include_fields: [field_name]
        }
      }).done(function(data) {
        return deferred.resolveWith(this, [data.objects[0][field_name]]);
      });
      return deferred.promise();
    }

    ajax_submit(options) {
      var done;
      if (options == null) {
        options = {};
      }
      if (options.type == null) {
        options.type = "POST";
      }
      if (options.url == null) {
        options.url = this.get_portal_url();
      }
      if (options.context == null) {
        options.context = this;
      }
      if (options.dataType == null) {
        options.dataType = "json";
      }
      if (options.data == null) {
        options.data = {};
      }
      this.debug("ajax_submit::options=", options);
      $(this).trigger("ajax:submit:start");
      done = function() {
        return $(this).trigger("ajax:submit:end");
      };
      return $.ajax(options).done(done);
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

}).call(this);
