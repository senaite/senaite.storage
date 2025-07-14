/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./components/store_container.js":
/*!***************************************!*\
  !*** ./components/store_container.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("{__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (__WEBPACK_DEFAULT_EXPORT__)\n/* harmony export */ });\n/* provided dependency */ var $ = __webpack_require__(/*! jquery */ \"jquery\");\nfunction _typeof(o) { \"@babel/helpers - typeof\"; return _typeof = \"function\" == typeof Symbol && \"symbol\" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && \"function\" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? \"symbol\" : typeof o; }, _typeof(o); }\nfunction _classCallCheck(a, n) { if (!(a instanceof n)) throw new TypeError(\"Cannot call a class as a function\"); }\nfunction _defineProperties(e, r) { for (var t = 0; t < r.length; t++) { var o = r[t]; o.enumerable = o.enumerable || !1, o.configurable = !0, \"value\" in o && (o.writable = !0), Object.defineProperty(e, _toPropertyKey(o.key), o); } }\nfunction _createClass(e, r, t) { return r && _defineProperties(e.prototype, r), t && _defineProperties(e, t), Object.defineProperty(e, \"prototype\", { writable: !1 }), e; }\nfunction _toPropertyKey(t) { var i = _toPrimitive(t, \"string\"); return \"symbol\" == _typeof(i) ? i : i + \"\"; }\nfunction _toPrimitive(t, r) { if (\"object\" != _typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || \"default\"); if (\"object\" != _typeof(i)) return i; throw new TypeError(\"@@toPrimitive must return a primitive value.\"); } return (\"string\" === r ? String : Number)(t); }\n/* Please use this command to compile this file into the proper folder:\n    coffee --no-header -w -o ../ -c store_container.coffee\n*/\nvar StoreContainerController;\nStoreContainerController = /*#__PURE__*/function () {\n  /*\n   * Store Samples in a Container view controller\n   */\n  function StoreContainerController() {\n    _classCallCheck(this, StoreContainerController);\n    this.bind_eventhandler = this.bind_eventhandler.bind(this);\n    this.on_position_change = this.on_position_change.bind(this);\n    this.on_position_slot_click = this.on_position_slot_click.bind(this);\n    this.debug = this.debug.bind(this);\n    console.debug(\"StoreContainerController::init\");\n    // bind the event handler to the elements\n    this.bind_eventhandler();\n    $(\"#position\").change();\n    return this;\n  }\n  return _createClass(StoreContainerController, [{\n    key: \"bind_eventhandler\",\n    value: function bind_eventhandler() {\n      this.debug(\"StoreContainerController::bind_eventhandler\");\n      $(\"body\").on(\"click\", \"a.position_slot_selector\", this.on_position_slot_click);\n      return $(\"body\").on(\"change\", \"#position\", this.on_position_change);\n    }\n  }, {\n    key: \"on_position_change\",\n    value: function on_position_change(event) {\n      var select;\n      /*\n       * The selected value from the position selected list has changed. Make the\n       * counterpart position selector from the layout more visible\n       */\n      this.debug(\"StoreContainerController::on_position_change\");\n      select = $(event.currentTarget);\n      $(\"td.empty-slot\").removeClass(\"selected\");\n      return $(\"#\" + select.val()).parent(\"td.empty-slot\").addClass(\"selected\");\n    }\n  }, {\n    key: \"on_position_slot_click\",\n    value: function on_position_slot_click(event) {\n      var anchor, sample_uid, select;\n      /*\n       * The user has clicked to a position slot from the layout. Update the\n       * value for position selection list and submit\n       */\n      this.debug(\"StoreContainerController::on_position_slot_click\");\n      event.preventDefault();\n      anchor = $(event.currentTarget);\n      select = $(\"#position\").val(anchor.attr(\"id\"));\n      $(\"#position\").change();\n      sample_uid = $(\"#sample_uid\").val();\n      if (sample_uid) {\n        return $(\"#button_store\").click();\n      }\n    }\n  }, {\n    key: \"debug\",\n    value: function debug(message) {\n      return console.debug(\"[senaite.storage] \" + message);\n    }\n  }]);\n}();\n/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (StoreContainerController);\n\n//# sourceURL=webpack:///./components/store_container.js?\n}");

/***/ }),

/***/ "./components/store_samples.js":
/*!*************************************!*\
  !*** ./components/store_samples.js ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("{__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (__WEBPACK_DEFAULT_EXPORT__)\n/* harmony export */ });\n/* provided dependency */ var $ = __webpack_require__(/*! jquery */ \"jquery\");\nfunction _typeof(o) { \"@babel/helpers - typeof\"; return _typeof = \"function\" == typeof Symbol && \"symbol\" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && \"function\" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? \"symbol\" : typeof o; }, _typeof(o); }\nfunction _classCallCheck(a, n) { if (!(a instanceof n)) throw new TypeError(\"Cannot call a class as a function\"); }\nfunction _defineProperties(e, r) { for (var t = 0; t < r.length; t++) { var o = r[t]; o.enumerable = o.enumerable || !1, o.configurable = !0, \"value\" in o && (o.writable = !0), Object.defineProperty(e, _toPropertyKey(o.key), o); } }\nfunction _createClass(e, r, t) { return r && _defineProperties(e.prototype, r), t && _defineProperties(e, t), Object.defineProperty(e, \"prototype\", { writable: !1 }), e; }\nfunction _toPropertyKey(t) { var i = _toPrimitive(t, \"string\"); return \"symbol\" == _typeof(i) ? i : i + \"\"; }\nfunction _toPrimitive(t, r) { if (\"object\" != _typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || \"default\"); if (\"object\" != _typeof(i)) return i; throw new TypeError(\"@@toPrimitive must return a primitive value.\"); } return (\"string\" === r ? String : Number)(t); }\n/* Please use this command to compile this file into the proper folder:\n    coffee --no-header -w -o ../ -c store_samples.coffee\n*/\nvar StoreSamplesController;\nStoreSamplesController = /*#__PURE__*/function () {\n  /*\n   * Store Samples view controller\n   */\n  function StoreSamplesController() {\n    _classCallCheck(this, StoreSamplesController);\n    this.bind_eventhandler = this.bind_eventhandler.bind(this);\n    this.on_container_change = this.on_container_change.bind(this);\n    this.on_container_position_change = this.on_container_position_change.bind(this);\n    this.add_container_position = this.add_container_position.bind(this);\n    this.purge_container_position = this.purge_container_position.bind(this);\n    this.get_container_position_selects = this.get_container_position_selects.bind(this);\n    this.fill_container_positions = this.fill_container_positions.bind(this);\n    this.diff = this.diff.bind(this);\n    this.get_selected_positions = this.get_selected_positions.bind(this);\n    this.fetch_available_positions = this.fetch_available_positions.bind(this);\n    this.ajax_submit = this.ajax_submit.bind(this);\n    this.get_portal_url = this.get_portal_url.bind(this);\n    this.debug = this.debug.bind(this);\n    console.debug(\"StoreSamplesController::init\");\n    // bind the event handler to the elements\n    this.bind_eventhandler();\n    return this;\n  }\n  return _createClass(StoreSamplesController, [{\n    key: \"bind_eventhandler\",\n    value: function bind_eventhandler() {\n      this.debug(\"StoreSamplesController::bind_eventhandler\");\n      $(\"body\").on(\"select\", \".senaite-uidreference-widget-input textarea\", this.on_container_change);\n      $(\"body\").on(\"deselect\", \".senaite-uidreference-widget-input textarea\", this.on_container_change);\n      return $(\"body\").on(\"change\", \"select[container_uid]\", this.on_container_position_change);\n    }\n  }, {\n    key: \"on_container_change\",\n    value: function on_container_change(event) {\n      var container_uid, el, parent, sample_uid, select;\n      /*\n       * Fills the select element next to the container input with the positions\n       * that are available for storage\n       */\n      this.debug(\"StoreSamplesController::on_container_change\");\n      el = $(event.currentTarget);\n      parent = el.closest(\"div.senaite-uidreference-widget-input\");\n      container_uid = event.detail.value;\n      sample_uid = parent.attr(\"sample_uid\");\n      select = $(\"select#sample_container_position_\".concat(sample_uid))[0];\n      this.fill_container_positions(container_uid, select);\n    }\n  }, {\n    key: \"on_container_position_change\",\n    value: function on_container_position_change(event) {\n      var container_uid, orig_value, position, select;\n      /*\n       * Purges the positions from other select elements that are bounded to\n       * same container. This ensures that a given position within a container can\n       * only be selected once\n       */\n      this.debug(\"StoreSamplesController::on_container_position_change\");\n      select = $(event.currentTarget);\n      container_uid = select.attr(\"container_uid\");\n      if (!container_uid) {\n        return;\n      }\n      position = select.val();\n      this.purge_container_position(container_uid, position);\n      orig_value = select.attr(\"original_value\");\n      $(select).attr(\"original_value\", position);\n      if (!orig_value) {\n        return;\n      }\n      return this.add_container_position(container_uid, orig_value);\n    }\n  }, {\n    key: \"add_container_position\",\n    value: function add_container_position(container_uid, position) {\n      var selects;\n      /*\n       * Adds the option for the specified position to all select elements that\n       * are bound to the container passed in that do not contain this position\n       * already\n       */\n      this.debug(\"StoreSamplesController::add_container_position:container_uid=\".concat(container_uid, \", position=\").concat(position));\n      selects = this.get_container_position_selects(container_uid);\n      $.each(selects, function (index, select) {\n        var options, orig_value, positions;\n        options = $(select).find(\"option\");\n        positions = $(options).map(function () {\n          return $(this).val();\n        });\n        positions = $.makeArray(positions);\n        if (positions.indexOf(position) >= 0) {\n          return;\n        }\n        positions.push(position);\n        positions.sort();\n        orig_value = $(select).val();\n        $(select).find(\"option\").remove();\n        $.each(positions, function (index, new_position) {\n          return $(select).append(new Option(new_position, new_position));\n        });\n        return $(select).val(orig_value);\n      });\n    }\n  }, {\n    key: \"purge_container_position\",\n    value: function purge_container_position(container_uid, position) {\n      var selects;\n      /*\n       * Removes the option for the specified position from all select elements\n       * that are bound to the container passed in. It only affects to those\n       * elements that have a position selected other than the one passed in.\n       */\n      this.debug(\"StoreSamplesController::purge_container_position:container_uid=\".concat(container_uid, \", position=\").concat(position));\n      selects = this.get_container_position_selects(container_uid);\n      $.each(selects, function (index, select) {\n        if ($(select).val() !== position) {\n          return $(select).find(\"option[value='\" + position + \"']\").remove();\n        }\n      });\n    }\n  }, {\n    key: \"get_container_position_selects\",\n    value: function get_container_position_selects(container_uid) {\n      /*\n       * Returns all DOM select elements for layout position selection that are\n       * bound to the container passed in\n       */\n      this.debug(\"StoreSamplesController::get_container_position_selects:container_uid=\".concat(container_uid));\n      return $(\"select[container_uid='\".concat(container_uid, \"']\"));\n    }\n  }, {\n    key: \"fill_container_positions\",\n    value: function fill_container_positions(container_uid, select) {\n      /*\n       * Populates the select DOM element with options that are the positions\n       * the container has available for storage. The first option is set as the\n       * default value for the select element and the rest of select elements for\n       * same container are updated accordingly to prevent same position to be\n       * assigned twice\n       */\n      this.debug(\"StoreSamplesController::fill_container_positions:container_uid=\".concat(container_uid));\n      $(select).find(\"option\").remove();\n      $(select).attr(\"original_value\", \"\");\n      $(select).attr(\"container_uid\", container_uid);\n      this.fetch_available_positions(container_uid).done(function (positions) {\n        var available, i, len, position, selected_positions;\n        selected_positions = this.get_selected_positions(container_uid);\n        available = this.diff(positions, $.makeArray(selected_positions));\n        for (i = 0, len = available.length; i < len; i++) {\n          position = available[i];\n          $(select).append(new Option(position, position));\n        }\n        $(select).val(available[0]);\n        $(select).trigger(\"change\");\n      }).fail(function () {\n        console.warn(\"Failed to get available positions\");\n      });\n    }\n  }, {\n    key: \"diff\",\n    value: function diff(a1, a2) {\n      /*\n       * Returns the difference (intersection) between two arrays\n       */\n      return a1.concat(a2).filter(function (val, index, arr) {\n        return arr.indexOf(val) === arr.lastIndexOf(val);\n      });\n    }\n  }, {\n    key: \"get_selected_positions\",\n    value: function get_selected_positions(container_uid) {\n      /*\n       * Return the positions that are currently selected in the form for a given\n       * container\n       */\n      var selects;\n      selects = this.get_container_position_selects(container_uid);\n      return $(selects).map(function () {\n        return $(this).val();\n      });\n    }\n  }, {\n    key: \"fetch_available_positions\",\n    value: function fetch_available_positions(uid) {\n      /*\n       * Returns the available positions from a sample container with the uid\n       * passed in. If no container found for this uid, returns null\n       */\n      var deferred, field_name;\n      deferred = $.Deferred();\n      field_name = \"AvailablePositions\";\n      this.ajax_submit({\n        url: this.get_portal_url() + \"/@@API/read\",\n        data: {\n          catalog_name: \"uid_catalog\",\n          UID: uid,\n          include_fields: [field_name]\n        }\n      }).done(function (data) {\n        return deferred.resolveWith(this, [data.objects[0][field_name]]);\n      });\n      return deferred.promise();\n    }\n  }, {\n    key: \"ajax_submit\",\n    value: function ajax_submit(options) {\n      var done;\n      if (options == null) {\n        options = {};\n      }\n      if (options.type == null) {\n        options.type = \"POST\";\n      }\n      if (options.url == null) {\n        options.url = this.get_portal_url();\n      }\n      if (options.context == null) {\n        options.context = this;\n      }\n      if (options.dataType == null) {\n        options.dataType = \"json\";\n      }\n      if (options.data == null) {\n        options.data = {};\n      }\n      this.debug(\"ajax_submit::options=\", options);\n      $(this).trigger(\"ajax:submit:start\");\n      done = function done() {\n        return $(this).trigger(\"ajax:submit:end\");\n      };\n      return $.ajax(options).done(done);\n    }\n  }, {\n    key: \"get_portal_url\",\n    value: function get_portal_url() {\n      /*\n       * Return the portal url (calculated in code)\n       */\n      var url;\n      url = $(\"input[name=portal_url]\").val();\n      return url || window.portal_url;\n    }\n  }, {\n    key: \"debug\",\n    value: function debug(message) {\n      return console.debug(\"[senaite.storage] \" + message);\n    }\n  }]);\n}();\n/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (StoreSamplesController);\n\n//# sourceURL=webpack:///./components/store_samples.js?\n}");

/***/ }),

/***/ "./scss/senaite.storage.scss":
/*!***********************************!*\
  !*** ./scss/senaite.storage.scss ***!
  \***********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("{__webpack_require__.r(__webpack_exports__);\n// extracted by mini-css-extract-plugin\n\n\n//# sourceURL=webpack:///./scss/senaite.storage.scss?\n}");

/***/ }),

/***/ "./senaite.storage.js":
/*!****************************!*\
  !*** ./senaite.storage.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("{__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _components_store_container_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./components/store_container.js */ \"./components/store_container.js\");\n/* harmony import */ var _components_store_samples_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./components/store_samples.js */ \"./components/store_samples.js\");\n\n\ndocument.addEventListener(\"DOMContentLoaded\", function () {\n  console.debug(\"*** SENAITE STORAGE JS LOADED ***\");\n\n  // Initialize controllers\n  var class_list = document.body.classList;\n  if (class_list.contains(\"template-storage_store_container\")) {\n    window.store_container_controller = new _components_store_container_js__WEBPACK_IMPORTED_MODULE_0__[\"default\"]();\n  }\n  if (class_list.contains(\"template-storage_store_samples\")) {\n    window.store_samples_controller = new _components_store_samples_js__WEBPACK_IMPORTED_MODULE_1__[\"default\"]();\n  }\n});\n\n//# sourceURL=webpack:///./senaite.storage.js?\n}");

/***/ }),

/***/ "jquery":
/*!*************************!*\
  !*** external "jQuery" ***!
  \*************************/
/***/ ((module) => {

module.exports = jQuery;

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	__webpack_require__("./senaite.storage.js");
/******/ 	var __webpack_exports__ = __webpack_require__("./scss/senaite.storage.scss");
/******/ 	
/******/ })()
;