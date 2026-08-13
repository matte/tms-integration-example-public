// <copyright file="TmsGatewayConfiguration.cs" company="Engaged Technologies">
// Copyright (c) Engaged Technologies. All rights reserved.
// </copyright>
// <summary>
//     Configuration class for TMS Gateway API
// </summary>

namespace TmsIntegrationExample.Services.TmsGatewayApi.Configuration
{
    public class TmsGatewayConfiguration
    {
        public System.Uri BaseAddress { get; set; }
        public string ShipmentsSubPath { get; set; }
        public string AccountNumber { get; set; }
    }
}
