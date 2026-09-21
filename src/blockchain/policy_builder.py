def policy_builder(policy_type:str, **kwargs):
    return {
        policy_type: {
            kwargs
        }
    }

