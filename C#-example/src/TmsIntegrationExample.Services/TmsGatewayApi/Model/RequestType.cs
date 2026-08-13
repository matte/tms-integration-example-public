// <copyright file="RequestType.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//    Shipment Request type.
// </summary>

namespace TmsIntegrationExample.Services.TmsGatewayApi.Model
{
    public enum RequestType
    {
        TRUCKLOAD = 1,

        EXPEDITE = 2,

        QUOTE_REQUESTED = 3,

        OPTIMIZE = 4,
    }
}
