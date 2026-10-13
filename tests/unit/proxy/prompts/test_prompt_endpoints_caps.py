# render-cap tests for /prompts/test jinja bounded globals (LD fork R1-M8)

from litellm.integrations.dotprompt.prompt_manager import PromptManager  # noqa


def _manager():
    from litellm.integrations.dotprompt.prompt_manager import PromptManager

    return PromptManager()


def test_small_range_still_renders():
    pm = _manager()
    out = pm.jinja_env.from_string("{{ range(10) | list }}").render()
    assert "[0, 1, 2" in out


def test_billion_loops_rejected():
    pm = _manager()
    import pytest

    with pytest.raises(ValueError) as exc:
        pm.jinja_env.from_string("{% for x in range(99999999999) %}{% endfor %}").render()
    assert "render cap" in str(exc.value)


def test_eager_materialization_rejected():
    pm = _manager()
    import pytest

    with pytest.raises(ValueError) as exc:
        pm.jinja_env.from_string("{{ range(2**61) | list }}").render()
    assert "render cap" in str(exc.value)

# render-cap tests for /prompts/test jinja bounded globals (LD fork R1-M8)

from litellm.integrations.dotprompt.prompt_manager import PromptManager  # noqa


def _manager():
    from litellm.integrations.dotprompt.prompt_manager import PromptManager

    return PromptManager()


def test_small_range_still_renders():
    pm = _manager()
    out = pm.jinja_env.from_string("{{ range(10) | list }}").render()
    assert "[0, 1, 2" in out


def test_billion_loops_rejected():
    pm = _manager()
    import pytest

    with pytest.raises(ValueError) as exc:
        pm.jinja_env.from_string("{% for x in range(99999999999) %}{% endfor %}").render()
    assert "render cap" in str(exc.value)


def test_eager_materialization_rejected():
    pm = _manager()
    import pytest

    with pytest.raises(ValueError) as exc:
        pm.jinja_env.from_string("{{ range(2**61) | list }}").render()
    assert "render cap" in str(exc.value)
