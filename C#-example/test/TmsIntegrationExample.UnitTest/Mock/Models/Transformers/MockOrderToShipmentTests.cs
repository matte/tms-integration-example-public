// <copyright file="MockOrderToShipmentTests.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     Tests for the MockOrderToShipmentTests class
// </summary>

namespace TmsIntegrationExample.UnitTest.Mock.Models.Transformers
{
    using System;
    using System.Collections.Generic;
    using FluentAssertions;
    using TmsIntegrationExample.Example.Transformers;
    using TmsIntegrationExample.Services.MockApi.Model;
    using TmsIntegrationExample.Services.TmsGatewayApi.Model;
    using Xunit;

    public class MockOrderToShipmentTests
    {
        [Fact]
        public void MockOrderToShipmentTransformAsExpected()
        {
            var order = new Order()
            {
                CustomerId = 19243,
                CompanyId = "BPH",
                LocationId = 13,
                PoNo = "240-23-0476",
                Taker = "ZACH_BALLARD",
                OrderDate = DateTime.Parse("2023-08-01T07:04:58.433"),
                RequestedDate = DateTime.Parse("2023-05-26T00:00:00"),
                Approved = false,
                ShipToId = 26412.0,
                ShipToName = "FOLEY PRODUCTS CO.",
                ShipToAddress1 = "1291 HARDIGREE ROAD",
                ShipToAddress2 = "WINDER, GA 30680-",
                ShipToAddress3 = "GA-BARROW",
                ShipToCity = "WINDER",
                OeHdrShip2State = "GA",
                ZipCode = "30680",
                ShipToCountry = "USA",
                SourceLocationId = 13,
                Route = "CON",
                PackingBasis = "Partial",
                Terms = "1",
                WillCall = "N",
                Class1id = "FIX BILL",
                Class2id = "QUARTER",
                RMA = "N",
                FreightCd = "PPD ADD",
                BillingDescription = "Standard",
                CaptureUsage = true,
                InvoiceBatchNumber = 3,
                InvoiceExchangeRateSource = "Order",
                ShipToPhone = "000-000-0000",
                ApplyBuilderAllowanceFlag = "N",
                CreateInvoice = false,
                MerchandiseCreditFlag = "N",
                RequiredPaymentUponRelease = "N",
                OrderNo = "1000267",
                PickTicketType = "UT",
                OeHdrUid = 260,
                ThirdPartyBilling = "S",
                CurrencyID = "1",
                Completed = "N",
                Quote = "N",
                DeletedFlag = "N",
                CancelledFlag = "N",
            };

            var shipTo = new Address();
            var sourceLocation = new Address();
            var accountNumber = "10800683";

            var expectedShipment = new ShipmentPost()
            {
                ShipmentStatus = "BUILDING",
                RequestedDeliveryDate = "5/26/2023 12:00:00 AM",
                ReferenceNumbers = new List<ReferenceNumber>()
                {
                    new ReferenceNumber()
                    {
                        Type = "SO_NUMBER",
                        Value = "1000267",
                    },
                    new ReferenceNumber()
                    {
                        Type = "PO_NUMBER",
                        Value = "240-23-0476",
                    },
                    new ReferenceNumber()
                    {
                        Type = "SHIPMENT_ID",
                        Value = "1000267",
                    },
                },
                IsComplete = false,
                AccountNumber = "10800683",
                Origin = new Stop()
                {
                    SendEmail = true,
                },
                Destination = new Stop()
                {
                    SendEmail = true,
                },
            };

            var result = new MockOrderToShipment().Transform(order, shipTo, sourceLocation, accountNumber);

            result.Should().BeEquivalentTo(expectedShipment);
        }

        [Fact]
        public void MockOrderToShipmentTransformFailsAsExpected()
        {
            var order = new Order()
            {
                CustomerId = 19243,
                CompanyId = "BPH",
                LocationId = 13,
                PoNo = "240-23-0476",
                Taker = "ZACH_BALLARD",
                OrderDate = DateTime.Parse("2023-08-01T07:04:58.433"),
                RequestedDate = DateTime.Parse("2023-05-26T00:00:00"),
                Approved = false,
                ShipToId = 26412.0,
                ShipToName = "FOLEY PRODUCTS CO.",
                ShipToAddress1 = "1291 HARDIGREE ROAD",
                ShipToAddress2 = "WINDER, GA 30680-",
                ShipToAddress3 = "GA-BARROW",
                ShipToCity = "WINDER",
                OeHdrShip2State = "GA",
                ZipCode = "30680",
                ShipToCountry = "USA",
                SourceLocationId = 13,
                Route = "CON",
                PackingBasis = "Partial",
                Terms = "1",
                WillCall = "N",
                Class1id = "FIX BILL",
                Class2id = "QUARTER",
                RMA = "N",
                FreightCd = "PPD ADD",
                BillingDescription = "Standard",
                CaptureUsage = true,
                InvoiceBatchNumber = 3,
                InvoiceExchangeRateSource = "Order",
                ShipToPhone = "000-000-0000",
                ApplyBuilderAllowanceFlag = "N",
                CreateInvoice = false,
                MerchandiseCreditFlag = "N",
                RequiredPaymentUponRelease = "N",
                OrderNo = "1000267",
                PickTicketType = "UT",
                OeHdrUid = 260,
                ThirdPartyBilling = "S",
                CurrencyID = "1",
                Completed = "N",
                Quote = "N",
                DeletedFlag = "N",
                CancelledFlag = "N",
            };

            var shipTo = new Address();
            var sourceLocation = new Address();
            var accountNumber = "10800683";

            var expectedShipment = new ShipmentPost()
            {
                ShipmentStatus = string.Empty,
                RequestedDeliveryDate = DateTime.Now.ToString(),
                ReferenceNumbers = new List<ReferenceNumber>()
                {
                    new ReferenceNumber()
                    {
                        Type = "SO_NUMBER",
                        Value = "1000267",
                    },
                    new ReferenceNumber()
                    {
                        Type = "PO_NUMBER",
                        Value = "240-23-0476",
                    },
                    new ReferenceNumber()
                    {
                        Type = "SHIPMENT_ID",
                        Value = "1000267",
                    },
                },
            };

            var result = new MockOrderToShipment().Transform(order, shipTo, sourceLocation, accountNumber);

            result.Should().NotBeEquivalentTo(expectedShipment);
        }
    }
}
