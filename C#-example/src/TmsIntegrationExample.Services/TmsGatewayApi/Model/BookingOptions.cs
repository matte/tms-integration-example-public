// <copyright file="BookingOptions.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//      This is the model that represents booking options for the shipment.
// </summary>

namespace TmsIntegrationExample.Services.TmsGatewayApi.Model
{
    using System;

    public class BookingOptions
    {
        public string SelectedReasonType { get; set; }

        public string SelectedReasonDescription { get; set; }

        public string ServiceLevel { get; set; }

        public Carrier Carrier { get; set; }

        public Guid SelectedRateId { get; set; }

        public bool Dispatch { get; set; }
    }
}
