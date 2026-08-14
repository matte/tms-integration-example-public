// <copyright file="Order.cs" company="Engaged Technologies">
//      Copyright (c) Engaged Technologies. All rights reserved.
//  </copyright>
// <summary>
//     This is the external representation of Order.
// </summary>

namespace TmsIntegrationExample.Services.MockApi.Model
{
    using System;

    public class Order
    {
        public int CustomerId { get; set; }

        public string CompanyId { get; set; }

        public int LocationId { get; set; }

        public string PoNo { get; set; }

        public string ContactId { get; set; }

        public string Taker { get; set; }

        public string JobName { get; set; }

        public DateTime? OrderDate { get; set; }

        public DateTime? RequestedDate { get; set; }

        public bool Approved { get; set; }

        public double? ShipToId { get; set; }

        public string ShipToName { get; set; }

        public string ShipToAddress1 { get; set; }

        public string ShipToAddress2 { get; set; }

        public string ShipToAddress3 { get; set; }

        public string ShipToCity { get; set; }

        public string OeHdrShip2State { get; set; }

        public string ZipCode { get; set; }

        public string ShipToCountry { get; set; }

        public string ShipToMailAddress { get; set; }

        public int SourceLocationId { get; set; }

        public int? CarrierId { get; set; }

        public string Route { get; set; }

        public string PackingBasis { get; set; }

        public string DeliveryInstructions { get; set; }

        public string Terms { get; set; }

        public string WillCall { get; set; }

        public string Class1id { get; set; }

        public string Class2id { get; set; }

        public string Class3id { get; set; }

        public string Class4id { get; set; }

        public string Class5id { get; set; }

        public string RMA { get; set; }

        public string FreightCd { get; set; }

        public string BillingDescription { get; set; }

        public bool CaptureUsage { get; set; }

        public string JobNo { get; set; }

        public int InvoiceBatchNumber { get; set; }

        public string InvoiceExchangeRateSource { get; set; }

        public string ShipToPhone { get; set; }

        public string ApplyBuilderAllowanceFlag { get; set; }

        public DateTime? QuoteExpirationDate { get; set; }

        public DateTime? PromiseDate { get; set; }

        public bool CreateInvoice { get; set; }

        public string CStrategicPriceLibraryId { get; set; }

        public string MerchandiseCreditFlag { get; set; }

        public string OrderPriorityId { get; set; }

        public string UpsCode { get; set; }

        public string PlacedByName { get; set; }

        public string RequiredPaymentUponRelease { get; set; }

        public decimal FreightOut { get; set; }

        public string OrderNo { get; set; }

        public string PickTicketType { get; set; }

        public int OeHdrUid { get; set; }

        public string ThirdPartyBilling { get; set; }

        public object UserDefinedFields { get; set; }

        public string CurrencyID { get; set; }

        public string Completed { get; set; }

        public string Quote { get; set; }

        public string DeletedFlag { get; set; }

        public string CancelledFlag { get; set; }

        public string InvoiceNo { get; set; }

        public object QuoteType { get; set; }

        public string WebReferenceNo { get; set; }
    }
}
