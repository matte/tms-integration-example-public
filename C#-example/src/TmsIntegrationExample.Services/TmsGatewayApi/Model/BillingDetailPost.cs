// <copyright file="BillingDetailPost.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//      Represents the Billing Detail on a shipment.
// </summary>

namespace TmsIntegrationExample.Services.TmsGatewayApi.Model
{
    public class BillingDetailPost
    {
        public string BillingType { get; set; }

        public string BillingPartyType { get; set; }

        public string BillingParty { get; set; }

        public string BillingAddress1 { get; set; }

        public string BillingAddress2 { get; set; }

        public string BillingCity { get; set; }

        public string BillingStateCode { get; set; }

        public string BillingPostalCode { get; set; }

        public string BillingCountryCode { get; set; }
    }
}
