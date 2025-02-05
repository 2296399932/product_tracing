from rest_framework import serializers
from .models import SalesStatistics, TracingStatistics, QualityAnalysis

class SalesStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesStatistics
        fields = '__all__'

class TracingStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TracingStatistics
        fields = '__all__'

class QualityAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = QualityAnalysis
        fields = '__all__' 