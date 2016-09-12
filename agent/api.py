class TariffCalculatorApi(View):
    def get(self, request):
        """
        Input:
        - from
        - to
        - weight
        - length
        - width
        - height

        Return
        A dictionary of 3 tariffs.
        - Progressif
        - Regressif
        - Volumetric
        """
        pass


class AwbGeneratorApi(View):
    def get(self, request):
        """Generate awb."""
        pass
