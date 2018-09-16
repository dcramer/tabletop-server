import graphene

from tabletop.models import Comment
from tabletop.schema import CheckinNode


class RemoveComment(graphene.Mutation):
    class Arguments:
        comment = graphene.UUID(required=True)

    ok = graphene.Boolean()
    errors = graphene.List(graphene.String)
    checkin = graphene.Field(CheckinNode)

    def mutate(self, info, comment: str = None):
        current_user = info.context.user
        if not current_user.is_authenticated:
            return RemoveComment(ok=False, errors=["Authentication required"])

        try:
            comment = Comment.objects.get(id=comment)
        except Comment.DoesNotExist:
            return RemoveComment(ok=False, errors=["Comment not found"])

        checkin = comment.checkin

        if (
            comment.created_by_id != current_user.id
            and checkin.created_by_id != current_user.id
        ):
            return RemoveComment(
                ok=False, errors=["Cannot remove comment from Checkin"]
            )

        comment.delete()

        return RemoveComment(ok=True, checkin=checkin)
