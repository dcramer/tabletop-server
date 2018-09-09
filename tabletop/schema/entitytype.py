import graphene


class EntityTypeEnum(graphene.Enum):
    publisher = "publisher"
    designer = "designer"
    artist = "artist"
