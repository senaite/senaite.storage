var UnmanagedEditController;

UnmanagedEditController = class UnmanagedEditController {
  /*
   * Toggle managed/unmanaged fields on StorageSamplesContainer forms
   */
  constructor() {
    this.init = this.init.bind(this);
    this.get_field = this.get_field.bind(this);
    this.get_input = this.get_input.bind(this);
    this.toggle_field = this.toggle_field.bind(this);
    this.toggle_fields = this.toggle_fields.bind(this);
    this.init();
    return this;
  }

  init() {
    var managed;
    managed = this.get_input("managed");
    if (!managed) {
      return;
    }
    managed.addEventListener("change", this.toggle_fields);
    this.toggle_fields();
  }

  get_field(name) {
    return document.getElementById("formfield-form-widgets-" + name) ||
      document.querySelector("[data-fieldname='" + name + "']") ||
      document.querySelector(".field." + name);
  }

  get_input(name) {
    var field;
    field = this.get_field(name);
    if (field) {
      return field.querySelector("input[type='checkbox']") ||
        field.querySelector("input[type='radio']") ||
        field.querySelector("select") ||
        field.querySelector("textarea") ||
        field.querySelector("input");
    }
    return document.querySelector("#form-widgets-" + name + "[type='checkbox']") ||
      document.querySelector("#form-widgets-" + name + "[type='radio']") ||
      document.getElementById("form-widgets-" + name) ||
      document.querySelector("[name='form.widgets." + name + "']") ||
      document.querySelector("[name='" + name + "']");
  }

  toggle_field(field, visible) {
    if (!field) {
      return;
    }
    field.classList.toggle("d-none", !visible);
  }

  toggle_fields() {
    var columns, isManaged, managed, physicalCapacity, rows;
    managed = this.get_input("managed");
    if (!managed) {
      return;
    }
    rows = this.get_field("rows");
    columns = this.get_field("columns");
    physicalCapacity = this.get_field("physical_capacity");
    isManaged = !!managed.checked;
    this.toggle_field(rows, isManaged);
    this.toggle_field(columns, isManaged);
    this.toggle_field(physicalCapacity, !isManaged);
  }
};

export default UnmanagedEditController;
