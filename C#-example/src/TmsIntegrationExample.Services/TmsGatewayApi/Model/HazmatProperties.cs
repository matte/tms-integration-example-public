// <copyright file="HazmatProperties.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//      The representation for hazmat properties on a shipment unit.
// </summary>

namespace TmsIntegrationExample.Services.TmsGatewayApi.Model
{
    public class HazmatProperties
    {
        public string UnNumber { get; set; }

        public string PackageGroup { get; set; }

        public string Class { get; set; }
    }
}
