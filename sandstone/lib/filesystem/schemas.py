import cerberus



class BaseObject:
    """
    Base object subclassed by all filesystem volume and object representations.
    Uses cerberus for data validation. Provides serializaiton and deserialization
    methods.
    """
    class ValidationError(Exception):
        pass

    schema = {
        'type': {
            'type': 'string',
            'allowed': ['volume','file','directory']
        },
        'name': {
            'type': 'string'
        },
        'owner': {
            'type': 'string'
        },
        'group': {
            'type': 'string'
        },
        'permissions': {
            'type': 'string',
            'regex': '^([r-][w-][x-]){3}$'
        },
        'size': {
            'type': 'string',
            'regex': '^([\d]+(.[\d]+)?[bKMGT])$'
        },
    }

    def __init__(self, *args, **kwargs):
        self.validator = cerberus.Validator(self.schema,allow_unknown=True)
        # Validate kwargs, then assign as members of instance
        try:
            self.validator.validate(kwargs)
        except DocumentError:
            raise ValidationError('Arguments do not match schema.')
        for k in kwargs.keys():
            setattr(self, k, kwargs.pop(k))

class VolumeObject(BaseObject):
    """
    This object standardizes the representation of filesystem volumes handled by
    the filesystem REST API.
    """

    schema = BaseObject.schema.update({
        'type': {
            'type': 'string',
            'allowed': ['volume']
        },
        'available_groups': {
            'type': 'list'
        },
        'fs_type': {
            'type': 'string'
        },
        'used': {
            'type': 'string',
            'regex': '^([\d]+(.[\d]+)?[bKMGT])$'
        },
        'used_pct': {
            'type': 'number',
            'min': 0,
            'max': 100
        }
    })

class FilesystemObject(BaseObject):
    """
    This object standardizes the representation of filesystem objects handled by
    the filesystem REST API.
    """

    schema = BaseObject.schema.update({
        'type': {
            'type': 'string',
            'allowed': ['file','directory']
        },
        'filepath': {
            'type': 'string'
        },
        'volume': {
            'type': 'string'
        }
    })
