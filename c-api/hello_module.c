#include <Python.h>

static PyObject* greet(PyObject* self, PyObject* args)
{
    const char* name;

    /* Parse the input, from Python string to C string */
    if (!PyArg_ParseTuple(args, "s", &name))
        return NULL;
    /* If the above function returns -1, an appropriate Python exception will
     * have been set, and the function simply returns NULL
     */

    printf("Hello %s\n", name);

    /* Returns a None Python object */
    Py_RETURN_NONE;
}

/* Define functions in module */
static PyMethodDef HelloMethods[] = {
    {"greet", greet, METH_VARARGS, "Greet somebody (in C)."},
    {NULL, NULL, 0, NULL}  /* Sentinel */
};

/* Create module definition */
static struct PyModuleDef helloModule = {
    PyModuleDef_HEAD_INIT,
    "hello",
    "",
    -1,
    HelloMethods,
    NULL,
    NULL,
    NULL,
    NULL
};


/* Module initialization */
// The initialization function must be named PyInit_name(), where name is the name of the module, 
// and should be the only non-static item defined in the module file
PyObject *PyInit_hello(void)
{
    return PyModule_Create(&helloModule);
}