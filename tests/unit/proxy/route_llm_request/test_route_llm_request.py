

def test_shared_deployment_credentials_are_not_tenant_scoped():
    """R2-1/R2-2: get_team_provider_credentials_with_scope reports team_owned
    True ONLY for the caller's own team's BYOK deployment — a shared
    deployment the caller may call is not one it owns, and raw-id guards
    consuming the merge must still demand admin for it."""
    import litellm
    from litellm.proxy._types import UserAPIKeyAuth
    from litellm.proxy.openai_files_endpoints.common_utils import (
        apply_team_provider_credentials,
        get_team_provider_credentials_with_scope,
    )

    shared_router = litellm.Router(
        model_list=[
            {"model_name": "gpt-4o", "litellm_params": {"model": "openai/gpt-4o", "api_key": "sk-shared"}}
        ]
    )
    team_router = litellm.Router(
        model_list=[
            {
                "model_name": "team-gpt",
                "litellm_params": {"model": "openai/gpt-4o", "api_key": "sk-team-byok"},
                "model_info": {"team_id": "team-123", "team_public_model_name": "team-gpt"},
            }
        ]
    )
    caller = UserAPIKeyAuth(user_id="u", team_id="team-123", models=[])

    creds, owned = get_team_provider_credentials_with_scope(
        llm_router=shared_router, user_api_key_dict=caller, custom_llm_provider="openai"
    )
    assert creds is not None and owned is False, "a shared deployment's credentials are not tenant-scoped"

    creds, owned = get_team_provider_credentials_with_scope(
        llm_router=team_router, user_api_key_dict=caller, custom_llm_provider="openai"
    )
    assert creds is not None and owned is True, "the team's own BYOK deployment is tenant-scoped"

    data: dict = {}
    merged = apply_team_provider_credentials(
        data=data, llm_router=shared_router, user_api_key_dict=caller, custom_llm_provider="openai"
    )
    assert merged is False and "api_key" in data  # merge still happens; the verdict is what guards consume
