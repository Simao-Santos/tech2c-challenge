from django.db import models

class EmissionRecord(models.Model):
    company = models.CharField(max_length=255)
    year = models.IntegerField()
    # Note
    sector = models.CharField(max_length=255)
    
    energy_consumption_mwh = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    co2_emissions_tons = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    class Meta:
        ordering = ["-year", "company"]
        verbose_name = "Emission Record"
        verbose_name_plural = "Emission Records"
        unique_together = ("company", "year", "sector")

    def __str__(self):
        return f"{self.company} – {self.year}"