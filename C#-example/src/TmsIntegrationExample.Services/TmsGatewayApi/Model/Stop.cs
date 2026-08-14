// <copyright file="Stop.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     The model that represents a shipment stop (origin, destination, etc.)
// </summary>

namespace TmsIntegrationExample.Services.TmsGatewayApi.Model
{
    using System.Collections.Generic;

    public class Stop
    {
        public string SpecialInstructions { get; set; }
        
        public bool SendEmail { get; set; }

        public string LocationDirectionType { get; set; }

        public string Name { get; set; }

        public string Address1 { get; set; }

        public string Address2 { get; set; }

        public string City { get; set; }

        public string StateCode { get; set; }

        public string PostalCode { get; set; }

        public string CountryCode { get; set; }

        public string OpenTime { get; set; }

        public string CloseTime { get; set; }

        public string ContactName { get; set; }

        public string ContactPhone { get; set; }

        public string ContactFax { get; set; }

        public List<string> ContactEmails { get; set; }
    }
}
