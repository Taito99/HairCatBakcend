from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from review.models import Review
from review.serializers import ReviewSerializer


class ReviewLikeDislikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({"message": "Review does not exist."}, status=404)

        action = request.data.get('action')

        if action == 'like':
            review.likes += 1
        elif action == 'dislike':
            review.dislikes += 1
        else:
            return Response({"message": "Invalid action."}, status=400)

        if request.user != review.user:  # Sprawdź, czy użytkownik jest autorem recenzji
            raise PermissionDenied("You are not allowed to like/dislike this review.")

        review.save()
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

@api_view(['GET'])
def get_all_reviews():
    review = Review.objects.all()
    serializer = ReviewSerializer(review, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addReview(request):
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['PUT'])
def updateReview(request, review_id):
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({"message": "Review does not exist."}, status=404)

    if request.user != review.user:
        raise PermissionDenied("You are not allowed to update this review.")

    serializer = ReviewSerializer(review, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)

@api_view(['DELETE'])
def deleteReview(request, review_id):
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({"message": "Review does not exist."}, status=404)

    if request.user != review.user:
        raise PermissionDenied("You are not allowed to delete this review.")

    review.delete()
    return Response({"message": "Review deleted successfully."}, status=204)