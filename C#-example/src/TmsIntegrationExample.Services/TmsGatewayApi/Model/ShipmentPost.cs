// <copyright file="ShipmentPost.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//      The representation for a POST shipment resource.
// </summary>

namespace TmsIntegrationExample.Services.TmsGatewayApi.Model
{
    using System.Collections.Generic;

    public class ShipmentPost
    {
        public string AccountNumber { get; set; }

        public string CarrierScac { get; set; }

        public bool IsComplete { get; set; }

        public string ShipmentStatus { get; set; }

        public bool Dispatch { get; set; }

        public string Mode { get; set; }

        public string EquipmentType { get; set; }

        public string ServiceLevel { get; set; }

        public string RequestedPickupDate { get; set; }

        public string RequestedDeliveryDate { get; set; }

        public Stop Origin { get; set; }

        public Stop Destination { get; set; }

        public ShipmentHazmatProperties Hazmat { get; set; }

        public BillingDetailPost BillingDetail { get; set; }

        public ICollection<Unit> Units { get; set; }

        public ICollection<Accessorial> Accessorials { get; set; }

        public ICollection<ReferenceNumber> ReferenceNumbers { get; set; }

        public BookingOptions BookingOptions { get; set; }
    }
}
