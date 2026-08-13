// <copyright file="ITmsGatewayClient.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     Interface for the TmsGateway Client
// </summary>

namespace TmsIntegrationExample.Services.TmsGatewayApi
{
    using System.Threading.Tasks;
    using TmsIntegrationExample.Services.TmsGatewayApi.Model;

    public interface ITmsGatewayClient
    {
        Task<Shipment> PostShipmentAsync(
            ShipmentPost shipment);
    }
}
