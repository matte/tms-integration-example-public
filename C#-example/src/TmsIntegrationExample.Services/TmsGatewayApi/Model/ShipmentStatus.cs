// <copyright file="ShipmentStatus.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     Shipment status.
// </summary>

namespace TmsIntegrationExample.Services.TmsGatewayApi.Model
{
    public enum ShipmentStatus
    {
        BUILDING = 1,

        BOOKED = 2,

        CANCELED = 3,

        OFFERED = 4,

        REQUESTED = 5,
    }
}
