#include <pybind11/pybind11.h>

int add(int i, int j) {
  return i + j;
}

namespace py = pybind11;

PYBIND11_MODULE(tensorstore, m) {
  m.doc() = R"pbdoc(
    tensorstore
    -----------

    .. currentmodule:: tensorstore

    .. autosummary::
       :toctree: _generate

       add
       subtract
  )pbdoc";

  m.attr("__version__") = VERSION_INFO;

  m.def("add", &add, R"pbdoc(
    Add two numbers

    Some other explanation about the add function.
  )pbdoc");

  m.def("subtract", [](int i, int j) { return i - j; }, R"pbdoc(
    Subtract two numbers

    Some other explanation about the subtract function.
  )pbdoc");
}
