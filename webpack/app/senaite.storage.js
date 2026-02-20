import StoreContainerController from "./components/store_container.js"
import StoreSamplesController from "./components/store_samples.js"
import ControlPanelController from "./components/controlpanel.js"

document.addEventListener("DOMContentLoaded", () => {
  console.debug("*** SENAITE STORAGE JS LOADED ***");

  // Initialize controllers
  var class_list = document.body.classList;
  if (class_list.contains("template-storage_store_container")) {
    window.store_container_controller = new StoreContainerController();
  }
  if (class_list.contains("template-storage_store_samples")) {
    window.store_samples_controller = new StoreSamplesController();
  }
  if (class_list.contains("template-storage-controlpanel")) {
    window.storage_controlpanel_controller = new ControlPanelController();
  }

});
