#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>
#include "logilinux/logilinux.h"
#include "logilinux/events.h"
#include "logilinux/device.h"
#include "logilinux/version.h"
#include "devices/mx_keypad_device.h"  // For MXKeypadDevice implementation

namespace py = pybind11;

PYBIND11_MODULE(_logilinux_native, m) {
    m.doc() = "Native C++ bindings for LogiLinux - Logitech device library for Linux";

    // Version info
    py::class_<LogiLinux::Version>(m, "Version")
        .def_readonly("major", &LogiLinux::Version::major)
        .def_readonly("minor", &LogiLinux::Version::minor)
        .def_readonly("patch", &LogiLinux::Version::patch)
        .def("__str__", [](const LogiLinux::Version &v) {
            return std::to_string(v.major) + "." + 
                   std::to_string(v.minor) + "." + 
                   std::to_string(v.patch);
        });

    // DeviceType enum
    py::enum_<LogiLinux::DeviceType>(m, "DeviceType")
        .value("UNKNOWN", LogiLinux::DeviceType::UNKNOWN)
        .value("DIALPAD", LogiLinux::DeviceType::DIALPAD)
        .value("MX_KEYPAD", LogiLinux::DeviceType::MX_KEYPAD)
        .export_values();

    // DeviceCapability enum
    py::enum_<LogiLinux::DeviceCapability>(m, "DeviceCapability")
        .value("ROTATION", LogiLinux::DeviceCapability::ROTATION)
        .value("BUTTONS", LogiLinux::DeviceCapability::BUTTONS)
        .value("HIGH_RES_SCROLL", LogiLinux::DeviceCapability::HIGH_RES_SCROLL)
        .value("LCD_DISPLAY", LogiLinux::DeviceCapability::LCD_DISPLAY)
        .value("IMAGE_UPLOAD", LogiLinux::DeviceCapability::IMAGE_UPLOAD)
        .export_values();

    // RotationType enum
    py::enum_<LogiLinux::RotationType>(m, "RotationType")
        .value("DIAL", LogiLinux::RotationType::DIAL)
        .value("WHEEL", LogiLinux::RotationType::WHEEL)
        .export_values();

    // DialpadButton enum
    py::enum_<LogiLinux::DialpadButton>(m, "DialpadButton")
        .value("TOP_LEFT", LogiLinux::DialpadButton::TOP_LEFT)
        .value("TOP_RIGHT", LogiLinux::DialpadButton::TOP_RIGHT)
        .value("BOTTOM_LEFT", LogiLinux::DialpadButton::BOTTOM_LEFT)
        .value("BOTTOM_RIGHT", LogiLinux::DialpadButton::BOTTOM_RIGHT)
        .value("UNKNOWN", LogiLinux::DialpadButton::UNKNOWN)
        .export_values();

    // MXKeypadButton enum
    py::enum_<LogiLinux::MXKeypadButton>(m, "MXKeypadButton")
        .value("GRID_0", LogiLinux::MXKeypadButton::GRID_0)
        .value("GRID_1", LogiLinux::MXKeypadButton::GRID_1)
        .value("GRID_2", LogiLinux::MXKeypadButton::GRID_2)
        .value("GRID_3", LogiLinux::MXKeypadButton::GRID_3)
        .value("GRID_4", LogiLinux::MXKeypadButton::GRID_4)
        .value("GRID_5", LogiLinux::MXKeypadButton::GRID_5)
        .value("GRID_6", LogiLinux::MXKeypadButton::GRID_6)
        .value("GRID_7", LogiLinux::MXKeypadButton::GRID_7)
        .value("GRID_8", LogiLinux::MXKeypadButton::GRID_8)
        .value("P1_LEFT", LogiLinux::MXKeypadButton::P1_LEFT)
        .value("P2_RIGHT", LogiLinux::MXKeypadButton::P2_RIGHT)
        .value("UNKNOWN", LogiLinux::MXKeypadButton::UNKNOWN)
        .export_values();

    // EventType enum
    py::enum_<LogiLinux::EventType>(m, "EventType")
        .value("ROTATION", LogiLinux::EventType::ROTATION)
        .value("BUTTON_PRESS", LogiLinux::EventType::BUTTON_PRESS)
        .value("BUTTON_RELEASE", LogiLinux::EventType::BUTTON_RELEASE)
        .value("DEVICE_CONNECTED", LogiLinux::EventType::DEVICE_CONNECTED)
        .value("DEVICE_DISCONNECTED", LogiLinux::EventType::DEVICE_DISCONNECTED)
        .export_values();

    // DeviceInfo struct
    py::class_<LogiLinux::DeviceInfo>(m, "DeviceInfo")
        .def_readonly("name", &LogiLinux::DeviceInfo::name)
        .def_readonly("device_path", &LogiLinux::DeviceInfo::device_path)
        .def_readonly("vendor_id", &LogiLinux::DeviceInfo::vendor_id)
        .def_readonly("product_id", &LogiLinux::DeviceInfo::product_id)
        .def_readonly("type", &LogiLinux::DeviceInfo::type);

    // Event base class
    py::class_<LogiLinux::Event, std::shared_ptr<LogiLinux::Event>>(m, "Event")
        .def_readonly("type", &LogiLinux::Event::type)
        .def_readonly("timestamp", &LogiLinux::Event::timestamp);

    // RotationEvent
    py::class_<LogiLinux::RotationEvent, LogiLinux::Event, 
               std::shared_ptr<LogiLinux::RotationEvent>>(m, "RotationEvent")
        .def_readonly("rotation_type", &LogiLinux::RotationEvent::rotation_type)
        .def_readonly("delta", &LogiLinux::RotationEvent::delta)
        .def_readonly("delta_high_res", &LogiLinux::RotationEvent::delta_high_res)
        .def_readonly("raw_event_code", &LogiLinux::RotationEvent::raw_event_code);

    // ButtonEvent
    py::class_<LogiLinux::ButtonEvent, LogiLinux::Event, 
               std::shared_ptr<LogiLinux::ButtonEvent>>(m, "ButtonEvent")
        .def_readonly("button_code", &LogiLinux::ButtonEvent::button_code)
        .def_readonly("pressed", &LogiLinux::ButtonEvent::pressed);

    // DeviceEvent
    py::class_<LogiLinux::DeviceEvent, LogiLinux::Event,
               std::shared_ptr<LogiLinux::DeviceEvent>>(m, "DeviceEvent")
        .def_readonly("device_path", &LogiLinux::DeviceEvent::device_path);

    // Device class (abstract base)
    py::class_<LogiLinux::Device, std::shared_ptr<LogiLinux::Device>>(m, "Device")
        .def("get_info", &LogiLinux::Device::getInfo, py::return_value_policy::reference)
        .def("get_type", &LogiLinux::Device::getType)
        .def("has_capability", &LogiLinux::Device::hasCapability)
        .def("set_event_callback", &LogiLinux::Device::setEventCallback)
        .def("start_monitoring", &LogiLinux::Device::startMonitoring)
        .def("stop_monitoring", &LogiLinux::Device::stopMonitoring)
        .def("is_monitoring", &LogiLinux::Device::isMonitoring)
        .def("grab_exclusive", &LogiLinux::Device::grabExclusive);

    // MXKeypadDevice - exposed for downcasting to access LCD functions
    py::class_<LogiLinux::MXKeypadDevice, LogiLinux::Device,
               std::shared_ptr<LogiLinux::MXKeypadDevice>>(m, "MXKeypadDevice")
        .def("set_key_image", &LogiLinux::MXKeypadDevice::setKeyImage)
        .def("set_key_color", &LogiLinux::MXKeypadDevice::setKeyColor)
        .def("initialize", &LogiLinux::MXKeypadDevice::initialize)
        .def("has_lcd", &LogiLinux::MXKeypadDevice::hasLCD);

    // Library class
    py::class_<LogiLinux::Library>(m, "Library")
        .def(py::init<>())
        .def("discover_devices", &LogiLinux::Library::discoverDevices)
        .def("find_device", &LogiLinux::Library::findDevice,
             py::arg("type"),
             "Find first device of specified type")
        .def("find_devices", &LogiLinux::Library::findDevices,
             py::arg("type"),
             "Find all devices of specified type")
        .def_static("get_version", &LogiLinux::Library::getVersion);

    // Helper functions for button enums
    m.def("get_dialpad_button", &LogiLinux::getDialpadButton,
          "Convert button code to DialpadButton enum");
    m.def("get_dialpad_button_name", &LogiLinux::getDialpadButtonName,
          "Get name of DialpadButton");
    m.def("get_mx_keypad_button", &LogiLinux::getMXKeypadButton,
          "Convert button code to MXKeypadButton enum");
    m.def("get_mx_keypad_button_name", &LogiLinux::getMXKeypadButtonName,
          "Get name of MXKeypadButton");
}
