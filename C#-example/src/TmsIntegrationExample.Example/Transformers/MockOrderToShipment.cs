// <copyright file="MockOrderToShipment.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//      Transforms Mock order to TMS Gateway shipment.
// </summary>

namespace TmsIntegrationExample.Example.Transformers
{
    using System.Collections.Generic;
    using TmsIntegrationExample.Services.MockApi.Model;
    using TmsIntegrationExample.Services.TmsGatewayApi.Model;

    public class MockOrderToShipment
    {
        public ShipmentPost Transform(Order from, Address shipTo, Address sourceLocation, string accountNumber)
        {
            if (from == null)
            {
                return null;
            }

            var referenceNumbers = new List<ReferenceNumber>();

            if (from.OrderNo != null)
            {
                var referenceSONumber = new ReferenceNumber()
                {
                    Type = "SO_NUMBER",
                    Value = from.OrderNo,
                };

                referenceNumbers.Add(referenceSONumber);

                var referenceShipmentId = new ReferenceNumber()
                {
                    Type = "SHIPMENT_ID",
                    Value = from.OrderNo,
                };
                referenceNumbers.Add(referenceShipmentId);
            }

            if (from.PoNo != null)
            {
                var referencePONumber = new ReferenceNumber()
                {
                    Type = "PO_NUMBER",
                    Value = from.PoNo,
                };
                referenceNumbers.Add(referencePONumber);
            }

            return new ShipmentPost
            {
                ShipmentStatus = "BUILDING",
                IsComplete = false,
                ReferenceNumbers = referenceNumbers,
                RequestedDeliveryDate = from.RequestedDate.ToString(),
                Origin = new MockAddressToGatewayStop().Transform(shipTo),
                Destination = new MockAddressToGatewayStop().Transform(sourceLocation),
                AccountNumber = accountNumber
            };
        }
    }
}
