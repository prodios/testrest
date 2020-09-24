from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from loanapps.serializers import ApplicationSerializer


class ApplicationAPIView(GenericAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = ApplicationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                'Заявка отправлена!',
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )