from exceptions import ConfigurationError

def test_configuration_error():
    exc = ConfigurationError("test")
    assert str(exc) ==  "Some required configurations are missing or not set properly: test"
    assert f"{exc}" == "Some required configurations are missing or not set properly: test"