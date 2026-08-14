// <copyright file="Unit.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//      The representation of a shipment handling unit
// </summary>

namespace TmsIntegrationExample.Services.TmsGatewayApi.Model
{
    public class Unit
    {
        public string FreightClass { get; set; }

        public string Description { get; set; }

        public int Quantity { get; set; }

        public decimal? Weight { get; set; }

        public string WeightUnitOfMeasure { get; set; }

        public string PackageType { get; set; }

        public string PalletType { get; set; }

        public bool IsStackable { get; set; }

        public HazmatProperties Hazmat { get; set; }

        public decimal? MonetaryValue { get; set; }

        public string Nmfc { get; set; }

        public string Sku { get; set; }

        public bool IsNew { get; set; }

        public int? ContainsQuantity { get; set; }

        public string ContainsDescription { get; set; }

        public decimal? Height { get; set; }

        public decimal? Width { get; set; }

        public decimal? Length { get; set; }

        public string DimensionsUnitOfMeasure { get; set; }
    }
}
