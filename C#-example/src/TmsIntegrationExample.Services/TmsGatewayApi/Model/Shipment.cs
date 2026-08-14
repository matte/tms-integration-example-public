// <copyright file="Shipment.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//      The representation for a shipment resource.
// </summary>

namespace TmsIntegrationExample.Services.TmsGatewayApi.Model
{
    using System;
    using System.Collections.Generic;

    public class Shipment
    {
        public Guid ShipmentId { get; set; }

        public Guid OrganizationId { get; set; }

        public Guid? CarrierId { get; set; }

        public string Name { get; set; }

        public string BillNumber { get; set; }

        public string TrackingNumber { get; set; }

        public string AccountNumber { get; set; }

        public string CarrierScac { get; set; }

        public string CarrierName { get; set; }

        public ShipmentStatus ShipmentStatus { get; set; }

        public bool IsComplete { get; set; }

        public bool Dispatch { get; set; }

        public Mode? Mode { get; set; }

        public EquipmentType? EquipmentType { get; set; }

        public ServiceLevel? ServiceLevel { get; set; }

        public FreightTerms? FreightTerms { get; set; }

        public string RequestedPickupDate { get; set; }

        public string RequestedDeliveryDate { get; set; }

        public Stop Origin { get; set; }

        public Stop Destination { get; set; }

        public ShipmentHazmatProperties Hazmat { get; set; }

        public BillingDetail BillingDetail { get; set; }

        public ICollection<Unit> Units { get; set; }

        public ICollection<Accessorial> Accessorials { get; set; }

        public ICollection<ReferenceNumber> ReferenceNumbers { get; set; }

        public Documents Documents { get; set; }

        public RequestType? RequestType { get; set; }

        public BookingOptions BookingOptions { get; set; }
    }
}
