#include <pybind11/pybind11.h>
#include <pybind11/functional.h>
#include <pybind11/stl.h>
#include "logilinux-driver/lib/include/logilinux/logilinux.h"
#include "logilinux-driver/lib/include/logilinux/events.h"
#include "logilinux-driver/lib/include/logilinux/device.h"

namespace py = pybind11;

PYBIND11_MODULE(logilinux, m) {
    m.doc() = "Python bindings for LogiLinux - Logitech device library for Linux";

    // DeviceType enum
    py::enum_<LogiLinux::DeviceType>(m, "DeviceType")
        .value("DIALPAD", LogiLinux::DeviceType::DIALPAD)
        .value("MX_KEYPAD", LogiLinux::DeviceType::MX_KEYPAD)
        .export_values();

    // Event base class
    py::class_<LogiLinux::Event, std::shared_ptr<LogiLinux::Event>>(m, "Event")
        .def_readonly("timestamp", &LogiLinux::Event::timestamp);

    // RotationEvent
    py::class_<LogiLinux::RotationEvent, LogiLinux::Event, std::shared_ptr<LogiLinux::RotationEvent>>(m, "RotationEvent")
        .def_readonly("delta", &LogiLinux::RotationEvent::delta)
        .def_readonly("angle", &LogiLinux::RotationEvent::angle);

    // ButtonEvent
    py::class_<LogiLinux::ButtonEvent, LogiLinux::Event, std::shared_ptr<LogiLinux::ButtonEvent>>(m, "ButtonEvent")
        .def_readonly("button_code", &LogiLinux::ButtonEvent::button_code)
        .def_readonly("pressed", &LogiLinux::ButtonEvent::pressed);

    // Device class
    py::class_<LogiLinux::Device, std::shared_ptr<LogiLinux::Device>>(m, "Device")
        .def("start_monitoring", &LogiLinux::Device::startMonitoring)
        .def("stop_monitoring", &LogiLinux::Device::stopMonitoring)
        .def("set_event_callback", &LogiLinux::Device::setEventCallback)
        .def("get_device_type", &LogiLinux::Device::getDeviceType);

    // Library class
    py::class_<LogiLinux::Library>(m, "Library")
        .def(py::init<>())
        .def("find_device", &LogiLinux::Library::findDevice,
             py::arg("type"),
             "Find a device by type");
}
